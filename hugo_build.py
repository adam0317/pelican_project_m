import os
from time import sleep
import boto3
import json
import subprocess
import requests
from dotenv import load_dotenv
from datetime import datetime
from air_table import add_new_record, get_ready_to_build_records, get_ready_to_deploy_records, get_records_to_add_to_cloudflare, search_table,  update_record
import ssl

from cloudflare import add_site_to_cloudflare, add_dns_to_cloudflare, add_page_rule, get_name_servers
from utils import combine_and_clean_kw_list, create_hugo_config, create_hugo_directory
ssl._create_default_https_context = ssl._create_unverified_context

import logging

import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('logs.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

load_dotenv()
current_working_dir = os.getcwd()
HUGO_BUILD_PATH = f"{os.getcwd()}/hugo_build_folder"
STAGING_PATH = os.getenv('STAGING_PATH', './staging')
HUGO_TEMPLATE_DIR = f'{os.path.join(current_working_dir, "hugo_template_site")}'
WASABI_ACCESS_KEY_ID = os.getenv('WASABI_ACCESS_KEY')
WASABI_SECRET_ACCESS_KEY = os.getenv('WASABI_SECRET_KEY')

def build_sites():  # sourcery no-metrics

    sites = get_ready_to_build_records()

    for record in sites:
        site = record['fields']
        start_date = site.get('start_date', None)
        domain = site['Base Domain']

        kw_list_exists = False

        for i in site['Keyword Lists']:
            kw_list_exists = os.path.exists(f'{os.getcwd()}/kw_lists/{i}.csv')
            if kw_list_exists:
                break
        if not kw_list_exists:
            combine_and_clean_kw_list(site)
        kw_list_path = f"{os.getcwd()}/kw_lists/{site['Keyword Lists'][0]}.csv"
        if 'Test' not in site['Status']:
            logging.debug(f"Starting Full Build {site['Bucket Name']}")
            update_record(record['id'], {'Status': 'In progress'})
        else:
            logging.debug(f"Starting Test Build {site['Bucket Name']}")

        spun_article_dir = f"{os.getcwd()}/spun_articles/{site['Article Name'][0].lower().replace(' ', '_')}"

        if not os.path.exists(spun_article_dir):
            os.makedirs(spun_article_dir)

        if len(os.listdir(spun_article_dir)) == 0:
            articles = site['article_file']
            if not articles:
                logging.info('*' * 80)
                logging.info(f'No Remote Article File Found For {domain}')
                logging.info('*' * 80)
                continue
            for article in articles:
                content = requests.get(article['url'])
                with open(f"{spun_article_dir}/{article['filename']}", 'w') as f:
                    f.write(content.text)

        build_dir = create_hugo_directory(domain)

        create_hugo_config(domain, build_dir, site['offer_link'][0])

        if 'Test' not in site['Status']:
            num_posts = '-1'
            subprocess.Popen(
                f"php spintax.php {kw_list_path} {spun_article_dir} {build_dir}/content/posts {num_posts} {start_date}", shell=True).wait()
        else:
            num_posts = '5'
            subprocess.Popen(
                f"php spintax.php {kw_list_path} {spun_article_dir} {build_dir}/content/posts {num_posts} {start_date}", shell=True).wait()

        subprocess.Popen(
            f"./hugo_build.sh {domain} {STAGING_PATH} {build_dir}", shell=True).wait()
        if 'Test' not in site['Status']:
            logging.info(f"Finished Full Build {site['Bucket Name']}")

            update_record(record['id'], {'Status': 'Ready To Deploy'})
        else:
            logging.info(f"Finished Test Build {site['Bucket Name']}")

        # upload zip to backup s3 bucket
        # Add the about/contact/disclaimer pages
    return

def handle_dns():
    sites = get_records_to_add_to_cloudflare()

    for record in sites:
        site = record['fields']
        domain = site['Base Domain']
        logging.info(f"Checking {domain} for DNS record")
        if not site.get('Bucket Created'):
            try:
                created = create_bucket(domain)
                if created:
                    update_record(record['id'], {'Bucket Created': True})
            except Exception as e:
                logging.info(e)
                continue
        if not site.get('Site Added To Cloudflare'):
            try:
                zone = add_site_to_cloudflare(domain)
                logging.info(zone)
                update_record(record['id'], {'Site Added To Cloudflare': True})
            except Exception as e:
                logging.info(e)
                continue
        if not site.get('DNS Added To Cloudflare'):
            try:
                add_dns_to_cloudflare(
                    domain, '@', f"{domain}.s3.us-west-1.wasabisys.com", True)
                add_dns_to_cloudflare(domain, 'www', domain, True)
                add_page_rule(domain)
                update_record(
                    record['id'], {'DNS Added To Cloudflare': True, 'Status': 'Ready To Build'})
            except Exception as e:
                logging.info(e)
                continue
        if not site.get('Nameservers'):
            name_servers = get_name_servers(domain)
            logging.info(name_servers)
            update_record(
                record['id'], {'Nameservers': ' '.join(name_servers)})
        sleep(1)

    return


def create_bucket(bucket_name):
    f"Creating bucket '{bucket_name}' with name '{bucket_name}'"
    session = boto3.Session(profile_name="wasabi")
    credentials = session.get_credentials()
    aws_access_key_id = credentials.access_key
    aws_secret_access_key = credentials.secret_key
    s3_resource = boto3.resource('s3', endpoint_url='https://s3.us-west-1.wasabisys.com', aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key, region_name='us-west-1')
    s3 = boto3.client('s3', endpoint_url='https://s3.us-west-1.wasabisys.com',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key, region_name='us-west-1')

    try:
        s3_resource.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
            'LocationConstraint': 'us-west-1'})
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }

        policy = json.dumps(policy)
        s3.put_bucket_policy(Bucket=bucket_name, Policy=policy)
        return True
    except Exception as e:
        logging.info(e)
        return False


def deploy_sites():
    sites = get_ready_to_deploy_records()
    for record in sites:
        date_time = datetime.now().strftime("%m/%d/%Y")
        domain_type = 'Root'
        site = record['fields']
        domain = site['Base Domain']
        logging.info(f"Deploying {domain} {date_time}")
        update_record(record['id'], {'Status': 'Deploying'})
        subprocess.Popen(
            f"./hugo_deploy.sh {domain}", shell=True).wait()

        live_site_record = {
            'Domain': site['Bucket Name'],
            'Date Built': date_time,
            'Offer': site['Offers'],
            'Server': site['Server'],
            'Domain Type': domain_type,
            'KW Lists': site['KW List ID']
        }
        if 'Test' not in site['Status']:
            existing_record = search_table(site['Bucket Name'])
            if existing_record:
                update_record(
                    existing_record[0]['id'], live_site_record, table='Live Sites')
            else:
                add_new_record(live_site_record)

        update_record(record['id'], {'Status': 'Need To Test'})


if __name__ == "__main__":
    if not os.path.exists(STAGING_PATH):
        os.makedirs(STAGING_PATH)


    build_step = input(
        'Choose a build step: \n1. dns\n2. build sites\n3. deploy_sites\n4. full run\n')

    if build_step == str(1):
        handle_dns()
    if build_step == str(2):
        build_sites()
    if build_step == str(3):
        deploy_sites()
    if build_step == str(4):
        handle_dns()
        build_sites()
        deploy_sites()

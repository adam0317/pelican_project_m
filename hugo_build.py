import sys
import logging
import os
import boto3
import json
import ssl
from subprocess import Popen, PIPE, STDOUT
from time import sleep
from dotenv import load_dotenv
from datetime import datetime
from air_table import add_new_record, get_ready_to_build_records, get_ready_to_deploy_records, get_records_to_add_to_cloudflare, search_table,  update_record
from article_forge import initiate_article, wait_for_article
from cloudflare import add_site_to_cloudflare, add_dns_to_cloudflare, add_page_rule, get_name_servers
from spin_articles import spin_articles
from spin_rw import spin_article
from utils import combine_and_clean_kw_list, create_hugo_config, create_hugo_directory
ssl._create_default_https_context = ssl._create_unverified_context


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


def check_io(process):
    while True:
        try:
            output = process.stdout.readline().decode()
            if output:
                logger.log(logging.INFO, output)
            else:
                break
        except:
            break


def build_sites():  # sourcery no-metrics

    sites = get_ready_to_build_records()

    for record in sites:
        site = record['fields']
        start_date = site.get('start_date', None)
        domain = site['Base Domain']

        kw_list_exists = False

        article_forge_keyword = site.get('article_forge_keyword')
        if not article_forge_keyword:
            logger.info(f"No Article Forge Keyword Found For {record['id']}")
            update_record(record['id'], {'Status': 'Error', 'Error Message':'No Article Forge Keyword Found'})
            continue
        article_forge_keyword_file_name = article_forge_keyword.replace(' ', '_').lower()
        kw_list = site['Keyword Lists'][0].replace(' ', '_').lower()
        
        kw_list_exists = os.path.exists(f'{os.getcwd()}/kw_lists/{kw_list}.csv')

        if kw_list_exists:
            num_keywords = sum(1 for line in open(f'{os.getcwd()}/kw_lists/{kw_list}.csv'))

        if not kw_list_exists:
            num_keywords = combine_and_clean_kw_list(site, kw_list)
        kw_list_path = f"{os.getcwd()}/kw_lists/{kw_list}.csv"
        update_record(record['id'], {'num_keywords': num_keywords})
        if 'Test' not in site['Status']:
            logging.debug(f"Starting Full Build {site['Bucket Name']}")
            update_record(record['id'], {'Status': 'In progress'})
        else:
            logging.debug(f"Starting Test Build {site['Bucket Name']}")
        

        # Create a new article and directory for the article
        # Check article forge for article
        
        article_path = f"{os.getcwd()}/articles/{article_forge_keyword_file_name}.txt"
        article_exists = os.path.exists(article_path)
        if not article_exists:
            # Check for ref key in site
            if site.get('article_forge_ref_key'):
                
                article_content = wait_for_article(site['article_forge_ref_key'])
                with open(article_path, 'w') as f:
                    f.write(article_content)
            else:
                article_forge_sub_keywords = site.get('article_forge_sub_keywords')
                article_forge_excluded_topics = site.get('article_forge_excluded_topics')
                # Get article from article forge
                ref_key = initiate_article(article_forge_keyword, sub_keywords=article_forge_sub_keywords, image=1, video=1, excluded_topics=article_forge_excluded_topics)
                update_record(record['id'], {'article_forge_ref_key': ref_key})
                article_content = wait_for_article(ref_key)
                with open(article_path, 'w') as f:
                        f.write(article_content)
                
        # check for spun version
        spun_article_dir = f"{os.getcwd()}/spun_articles/{article_forge_keyword_file_name}"
        spun_article_path = f"{spun_article_dir}/{article_forge_keyword_file_name}.txt"
        spun_article_exists = os.path.exists(spun_article_path)
        if not spun_article_exists:
            # Spin article
            if not os.path.exists(spun_article_dir):
                os.makedirs(spun_article_dir)
            spun_article = spin_article(article_path)
            with open(spun_article_path, 'w') as f:
                f.write(spun_article)

        build_dir = create_hugo_directory(domain)

        create_hugo_config(domain, build_dir, site['offer_link'][0])


        if 'Test' not in site['Status']:
            num_posts = '-1'
        else:
            num_posts = '5'
            
        spin_articles(kw_list_path, spun_article_dir, build_dir, num_posts, start_date)

        process = Popen(
            f"./hugo_build.sh {domain} {STAGING_PATH} {build_dir}", shell=True)
        while process.poll() is None:
            check_io(process)

        if 'Test' not in site['Status']:
            logging.info(f"Finished Full Build {site['Bucket Name']}")
            update_record(record['id'], {'Status': 'Ready To Deploy'})
        else:
            logging.info(f"Finished Test Build {site['Bucket Name']}")


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
        update_record(record['id'], {'Status': 'Ready To Build'})
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
        Popen(
            f"./hugo_deploy.sh {domain}", shell=True).wait()

        live_site_record = {
            'Domain': site['Bucket Name'],
            'Date Built': date_time,
            'Offer': site['Offers'],
            'Server': site['Server'],
            'Domain Type': domain_type,
            'KW Lists': site['KW List ID'],
            'Pages': site['num_keywords'],
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

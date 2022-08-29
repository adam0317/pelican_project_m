# from cloudflare import add_site_to_cloudflare, add_dns_to_cloudflare
# import sthree
import csv
import os
from time import sleep
import boto3
import json
import subprocess
from dotenv import load_dotenv
from spin_rw import spin_article
from datetime import datetime
from air_table import add_new_record, get_ready_to_build_records, get_ready_to_deploy_records, get_records_to_add_to_cloudflare, search_table,  update_record
import article_forge
# from build_pages import multi_thread_posts, add_base_pages
import pandas as pd
import ssl
import shutil
from ruamel.yaml import YAML
from cloudflare import add_site_to_cloudflare, add_dns_to_cloudflare, add_page_rule, get_name_servers
ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
yaml = YAML()
current_working_dir = os.getcwd()
HUGO_BUILD_PATH = f"{os.getcwd()}/hugo_build_folder"
STAGING_PATH = os.getenv('STAGING_PATH', '../staging')
HUGO_TEMPLATE_DIR = f'{os.path.join(current_working_dir, "hugo_template_site")}'
WASABI_ACCESS_KEY_ID = os.getenv('WASABI_ACCESS_KEY')
WASABI_SECRET_ACCESS_KEY = os.getenv('WASABI_SECRET_KEY')


def send_article_to_spin_rewriter(keyword):
    article_to_spin = f"./new_articles/{keyword}.txt"
    spin_article(article_to_spin, keyword)
    return


def create_hugo_directory(domain_name):
    new_dir = f'{HUGO_BUILD_PATH}/campaigns/{domain_name}'
    print(f'{os.path.join(current_working_dir, new_dir)}')
    if os.path.exists(new_dir):
        print("removing existing directory")
        shutil.rmtree(new_dir)
    shutil.copytree(HUGO_TEMPLATE_DIR, new_dir)
    return new_dir


def build_sites():  # sourcery no-metrics

    sites = get_ready_to_build_records()

    for record in sites:
        site = record['fields']
        start_date = site['start_date']
        domain = site['Base Domain']

        kw_list_exists = False
        for i in site['Keyword Lists']:
            kw_list_exists = os.path.exists(f'{os.getcwd()}/kw_lists/{i}.csv')
            if kw_list_exists:
                break
        if not kw_list_exists:
            print('No KW List Found')
            df = pd.read_csv(f"{site['csv_file'][0]['url']}")
            df.to_csv(
                f"{os.getcwd()}/kw_lists/{site['csv_file'][0]['filename']}", index=False)
        kw_list_path = f"{os.getcwd()}/kw_lists/{site['csv_file'][0]['filename']}"
        print(f"Starting Full Build {site['Bucket Name']}")
        if 'Test' not in site['Status']:
            update_record(record['id'], {'Status': 'In progress'})

        spun_article_dir = f"{os.getcwd()}/spun_articles/{site['Article'][0].lower()}"

        if not os.path.exists(spun_article_dir):
            print('*' * 80)
            print(f'No Article Directory Found For {domain}')
            print('*' * 80)
            # Get an article from article_forge

            continue
        elif len(os.listdir(spun_article_dir)) == 0:
            print('*' * 80)
            print(f'No Article Found For {domain}')
            print('*' * 80)
            continue

        build_dir = create_hugo_directory(domain)

        create_hugo_config(domain, build_dir, site['offer_link'][0])
        subprocess.Popen(
            f"php spintax.php {kw_list_path} {spun_article_dir} {build_dir}/content/posts {start_date}", shell=True).wait()

        subprocess.Popen(
            f"./hugo_build.sh {domain} {STAGING_PATH} {build_dir}", shell=True).wait()

        update_record(record['id'], {'Status': 'Ready To Deploy'})

        # Article Forge Integration
        # upload zip to backup s3 bucket
    return


def create_hugo_config(domain, dst_dir, offer_link):

    yaml_file_dict = {
        'baseURL': '', 'menu': {'main':
                                [{'identifier': 'contact', 'name': 'contact', 'url': 'contact/', 'weight': 10}, {'identifier': 'disclaimer', 'name': 'disclaimer', 'url': 'disclaimer/', 'weight': 20}, {
                                    'identifier': 'privacy', 'name': 'privacy', 'url': 'privacy/', 'weight': 30}, {'identifier': 'sitemap', 'name': 'sitemap', 'url': '/sitemap.xml', 'weight': 40}]

                                # , 'umami': domain.uuid
                                # , 'umamiUrl': 'https://umami-vercel-chi.vercel.app/umami.js'
                                }, 'title': domain, 'paginate': 5, 'theme': 'PaperMod', 'enableRobotsTXT': True, 'buildDrafts': False, 'buildFuture': False, 'buildExpired': False, 'minify': {'disableXML': True, 'minifyOutput': True}, 'params': {'hideFooter': True, 'env': 'production', 'title': domain, 'custom_js': ['/js/custom.js'], 'description': domain, 'DateFormat': 'January 2, 2006', 'defaultTheme': 'auto', 'disableThemeToggle': False, 'ShowReadingTime': True, 'ShowShareButtons': True, 'ShowPostNavLinks': True, 'ShowBreadCrumbs': True, 'ShowCodeCopyButtons': False, 'ShowWordCount': True, 'ShowRssButtonInSectionTermList': True, 'UseHugoToc': True, 'disableSpecial1stPost': False, 'disableScrollToTop': False, 'comments': False, 'hidemeta': False, 'hideSummary': False, 'showtoc': False, 'tocopen': False, 'label': {'text': f'Welcome to {domain}', 'icon': '/apple-touch-icon.png', 'iconHeight': 35}, 'cover': {'hidden': True, 'hiddenInList': True, 'hiddenInSingle': True}

                                                                                                                                                                                                                                                      }}
    with open(f'{dst_dir}/config/_default/config.yaml', 'w') as yaml_file:
        docs = yaml.dump(yaml_file_dict, yaml_file)
    offer_link = f"{offer_link}/{domain.replace('.', '')}"
    with open(f'{dst_dir}/static/js/custom.js', 'w') as js_file:
        js_file.write(redir_script.replace('{{ offer_link }}', offer_link))
    return


redir_script = """
const urlParams = new URLSearchParams(window.location.search);
const redir = urlParams.get("redir");
const currentHost = window.location.href;
console.log(currentHost);
// const currentDomain = window.location.host
if (!redir) {
  if (!currentHost.includes("localhost")) {
    let agents = [
      "goog",
      "bot",
      "slurp",
      "msn",
      "scooter",
      "yahoo",
      "crawler",
      "media",
      "bing",
      "ask",
    ];
    found = agents.findIndex((element) =>
      navigator.userAgent.toLowerCase().includes(element)
    );

    if (found < 0) {
      let offer_link = "{{ offer_link }}";

      if (offer_link.includes("?")) {
        offer_link = offer_link + "&referring_url=" + window.location.href;
      } else {
        offer_link = offer_link + "?referring_url=" + window.location.href;
      }

      window.location.replace(encodeURI(offer_link));
    }
  }
}
"""


def handle_dns():
    sites = get_records_to_add_to_cloudflare()

    for record in sites:
        site = record['fields']
        domain = site['Base Domain']
        print(f"Checking {domain} for DNS record")
        if not site.get('Bucket Created'):
            try:
                created = create_bucket(domain)
                if created:
                    update_record(record['id'], {'Bucket Created': True})
            except Exception as e:
                print(e)
                continue
        if not site.get('Site Added To Cloudflare'):
            try:
                zone = add_site_to_cloudflare(domain)
                print(zone)
                update_record(record['id'], {'Site Added To Cloudflare': True})
            except Exception as e:
                print(e)
                continue
        if not site.get('DNS Added To Cloudflare'):
            try:
                add_dns_to_cloudflare(
                    domain, '@', f"{domain}.s3.us-west-1.wasabisys.com", True)
                add_dns_to_cloudflare(domain, 'www', domain, True)
                add_page_rule(domain)
                update_record(record['id'], {'DNS Added To Cloudflare': True, 'Status': 'Ready To Build'})
            except Exception as e:
                print(e)
                continue
        if not site.get('Nameservers'):
            name_servers = get_name_servers(domain)
            print(name_servers)
            update_record(record['id'], {'Nameservers': ' '.join(name_servers)})
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
        print(e)
        return False


def deploy_sites():
    sites = get_ready_to_deploy_records()
    for record in sites:
        date_time = datetime.now().strftime("%m/%d/%Y")
        domain_type = 'Root'
        site = record['fields']
        domain = site['Base Domain']
        print(f"Deploying {domain} {date_time}")
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

    handle_dns()
    build_sites()
    deploy_sites()

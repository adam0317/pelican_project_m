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

# List of things to do:
# 1. Get all records from Strapi that are ready to build
# 2. For each record, get content if needed
# 3. Spin content if needed
# 4. Clean and combine keywords if needed
# 5. Create Pelican config file
# 6. Create Pelican directory
# 7. Build Pelican site
# 8. Upload Pelican site to Wasabi

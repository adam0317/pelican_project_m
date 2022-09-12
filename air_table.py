import os
from airtable import Airtable
from dotenv import load_dotenv
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
load_dotenv()

AIR_TABLE_API_KEY = os.getenv('AIR_TABLE_API_KEY')
base_id = 'appI5YlCf5EOpYBsi'
table_name = 'Build Step'

headers = {"Authorization": f"Bearer {AIR_TABLE_API_KEY}"}

url = f"https://api.airtable.com/v0/{base_id}/{table_name}"

build_table = Airtable(base_id, table_name, AIR_TABLE_API_KEY)
live_sites = Airtable(base_id, 'Live Sites', AIR_TABLE_API_KEY)


def get_ready_to_build_records():
    x = build_table.get_all(view='Ready To Build')
    return x

def get_records_to_add_to_cloudflare():
    x = build_table.get_all(view='Add To Cloudflare')
    return x

def get_ready_to_deploy_records():
    x = build_table.get_all(view='Ready To Deploy')
    return x

def get_ready_to_test_records():
    x = build_table.get_all(view='Need To Test')
    return x


def get_all_site_records(view='All Sites'):
    x = live_sites.get_all(view=view)
    return x


def search_table(value, field='Domain', table='Live Sites'):
    x = Airtable(base_id, table, AIR_TABLE_API_KEY)
    return x.search(field, value)


def update_record(id, fields, table='Build Step'):
    x = Airtable(base_id, table, AIR_TABLE_API_KEY)
    x.update(id, fields)

def get_single_build_record(id):
    return build_table.get(id)
    


def add_new_record(record, table='Live Sites'):
    x = Airtable(base_id, table, AIR_TABLE_API_KEY)
    new_record = x.insert(record)
    print(new_record)
    return new_record

if __name__ == '__main__':
    import pandas as pd
    import requests
    sites = get_ready_to_build_records()
    for record in sites:
        site = record['fields']
        kw_list_exists = False
        kw_urls = []
        domain = site['Base Domain']
        print(site)
        spun_article_dir = f"{os.getcwd()}/spun_articles/{site['Article Name'][0].lower()}"
        print(spun_article_dir)
        if not os.path.exists(spun_article_dir):
            print('*' * 80)
            print(f'No Article Directory Found For ')
            print('*' * 80)
            os.makedirs(spun_article_dir)
        if len(os.listdir(spun_article_dir)) == 0:
            print('*' * 80)
            print(f'No Local Article Found For {domain}')
            print('*' * 80)
            articles = site['article_file']
            if not articles:
                print(f'No Remote Article File Found For {domain}')
                print('*' * 80)
                continue
            for article in articles:
                
                content = requests.get(article['url'])
                with open(f"{spun_article_dir}/{article['filename']}", 'w') as f:
                    f.write(content.text)
    pass
# update_record('recthzunpCHtplft2', {'Status': 'Do Not Build'})
# add_live_site(site)

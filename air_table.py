import os
from airtable import Airtable
from dotenv import load_dotenv
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
    # get_ready_to_build_records()
    pass
# update_record('recthzunpCHtplft2', {'Status': 'Do Not Build'})
# add_live_site(site)

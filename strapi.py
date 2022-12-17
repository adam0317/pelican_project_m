import requests
import os
import json
import pandas as pd

from utils import combine_and_clean_kw_list

BASE_STRAPI_URL = os.getenv('BASE_STRAPI_URL', 'http://localhost:1337')
BASE_STRAPI_API_URL = f"{BASE_STRAPI_URL}/api"

def pretty_print_request(json_data):
    print(json.dumps(json_data, indent=2))

def strapi_combine_and_clean_kw_list(url_list, file_name):
    """Combine all the keywords into one clean list and remove duplicates."""

    df = pd.concat([pd.read_csv(f) for f in url_list])
    df = df.drop_duplicates(subset='Keyword')
    df = df.dropna(subset=['Keyword'])
    df = df.reset_index(drop=True)
    # remove any characters that are not letters, numbers, or spaces
    df['Keyword'] = df['Keyword'].str.replace(r'[^a-zA-Z0-9\s]', '')
    # remove any keywords that are just numbers
    df = df[~df['Keyword'].str.isnumeric()]
    # remove any keywords that are less than 3 characters
    df = df[df['Keyword'].str.len() > 2]
    # remove any keywords that are just spaces
    df = df[~df['Keyword'].str.isspace()]
    # remove any keywords that are to long for a url
    df = df[df['Keyword'].str.len() < 75]
    # change to title case
    combined_csv = df['Keyword'].str.title().strip()
    print(combined_csv.head())
    # save to csv
    # combined_csv.to_csv(index=False)
    files = {'files': (f"{file_name.lower()}_clean_combined.csv", combined_csv.to_csv(index=False))}
    r = requests.post(f"{BASE_STRAPI_URL}/api/upload", files=files)
    print(r.json())
    kw_list_id = r.json()[0]['id']
    # get length of combined csv
    kw_list_length = len(combined_csv)
    print(f"Combined CSV length: {kw_list_length}")
    return kw_list_length, kw_list_id
    

def get_many(endpoint, filters=None):
    url = f"{BASE_STRAPI_API_URL}/{endpoint}"
    query_string = "populate=*"
    if filters:
        for key, value in filters.items():
            filters[key] = f"{key}={value}"
            query_string += f"&{key}={value}"
    url = f"{url}?{query_string}"
    response = requests.get(url)

    return response.json()

def get_one(endpoint, id):
    url = f"{BASE_STRAPI_API_URL}/{endpoint}/{id}?populate=*"
    response = requests.get(url)
    return response.json()

def update_one(endpoint, id, data):
    url = f"{BASE_STRAPI_API_URL}/{endpoint}/{id}"
    payload = {
        "data": {
            "num_clean_keywords": data['num_clean_keywords'],
            "clean_and_combined_kw_lists": data['clean_and_combined_kw_lists']
    }
    }
    print(payload)
    response = requests.put(url, json=payload)
    print(response.json())
    return response.json()

def download_media(file_name):
    url = f"{BASE_STRAPI_URL}/uploads/{file_name}"
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    campaigns = get_many("campaigns")
    # pretty_print_request(campaigns)
    for campaign in campaigns['data']:
        single_campaign = get_one("campaigns", campaign["id"])
        # pretty_print_request(single_campaign)
        kw_list_ids = [x['id'] for x in single_campaign['data']['attributes']['keyword_lists']['data']]
        # print(kw_list_ids)
        kw_list_data = get_many("keyword-lists", {"id_in": kw_list_ids})
        # pretty_print_request(kw_list_data)
        for kw_list in kw_list_data['data']:
            if kw_list['attributes']['clean_and_combined_kw_lists']['data'] == None:
                url_list = [f"{BASE_STRAPI_URL}{x['attributes']['url']}" for x in kw_list['attributes']['raw_kw_lists']['data']]
                kw_list_length, new_media_library_kw_list_id = strapi_combine_and_clean_kw_list(url_list, kw_list['attributes']['name'])
                update_one("keyword-lists", kw_list['id'], {"num_clean_keywords": kw_list_length, "clean_and_combined_kw_lists": new_media_library_kw_list_id})
      
                # http://localhost:1337/uploads/baby_cosleeping_broad_match_us_2022_07_09_0243247641.csv?updated_at=2022-12-17T19:58:26.458Z
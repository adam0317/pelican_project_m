import requests
import os
from dotenv import load_dotenv, find_dotenv
import json
load_dotenv(find_dotenv())

ARTICLE_FORGE_API_KEY = os.environ.get('ARTICLE_FORGE_API_KEY')
BASE_URL = 'https://af.articleforge.com/api'


def initiate_article(keyword, sub_keywords=None, length='long', image=1, video=1, excluded_topics=None):
    data = json.dumps({
        'key': ARTICLE_FORGE_API_KEY,
        'keyword': keyword,
        'sub_keywords': sub_keywords,
        'length': length,
        'image': image,
        'video': video,
        'excluded_topics': excluded_topics
    })
    print(f"Initiating article for {keyword}")
    print(f"Data: {data}")

    r = requests.post(f'{BASE_URL}/initiate_article', data=data)
    print(r.json())
    if r.json()['status'] == 'Success':
        ref_key = r.json()['ref_key']
        return ref_key
    else:
        return False


def get_article_status(ref_key):
    r = requests.post(f'{BASE_URL}/get_api_progress',
                      data=json.dumps({'key': ARTICLE_FORGE_API_KEY, 'ref_key': ref_key}))
    progress = r.json()['progress']
    return progress


def get_finished_article(ref_key):
    r = requests.post(f'{BASE_URL}/get_api_article_result',
                      data=json.dumps({'key': ARTICLE_FORGE_API_KEY, 'ref_key': ref_key}))
    return r.json()


def view_articles():
    r = requests.post(f'{BASE_URL}/view_articles',
                      data=json.dumps({'key': ARTICLE_FORGE_API_KEY}))
    for i in r.json()['data']:
        print(i)


if __name__ == '__main__':
    import time
    # it can be either 'very_short'(approximately 50 words), 'short'(approximately 250 words),
    # 'medium'(approximately 500 words), 'long'(approximately 750 words), or 'very_long'(approximately 1,500 words).
    ref_key = initiate_article('Builderall Vs Kartra', sub_keywords='Website Builder, Funnel',
                               image=1, video=1, length='short')
# ref_key = 268025801

    waiting_for_article = True
    while waiting_for_article:
        if get_article_status(ref_key) != 1:
            print('Article is not ready yet, waiting 30 seconds...')
            time.sleep(30)
        else:
            waiting_for_article = False
    finished_article = get_finished_article(ref_key)
    finished_article['status']
    finished_article['article']
    finished_article['article_id']

    with open('./new_articles/test1.txt', 'w') as output_file:
        output_file.write(finished_article['article'])
# get_article_status(268063475)
# get_finished_article(208174327)

# sub_keywords = None

# if site.get('Sub Keywords'):
#     sub_keywords = site.get('Sub Keywords')
# ref_key = article_forge.initiate_article(site['Article'], sub_keywords=sub_keywords)
# if not ref_key:
#     continue
# waiting_for_article = True
# while waiting_for_article:
#     time.sleep(30)
#     progress = article_forge.get_article_status(ref_key)
#     if progress != 1:
#         print(f'Waiting for article {progress}')
#     else:
#         waiting_for_article = False
# print('Article Completed')
# # new_article_record = add_new_record(finished_article, 'Articles')
# update_record(record['id'], {'ref_key': ref_key})
# finished_article = article_forge.get_finished_article(ref_key)
# with open(f"./new_articles/{site['Article']}.txt", 'w') as output_file:
#     output_file.write(finished_article['article'])

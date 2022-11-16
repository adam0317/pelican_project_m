import pandas as pd
import os
from spin_rw import spin_article
import logging
import shutil
import yaml


current_working_dir = os.getcwd()
HUGO_BUILD_PATH = f"{os.getcwd()}/hugo_build_folder"
STAGING_PATH = os.getenv('STAGING_PATH', './staging')
HUGO_TEMPLATE_DIR = f'{os.path.join(current_working_dir, "hugo_template_site")}'
WASABI_ACCESS_KEY_ID = os.getenv('WASABI_ACCESS_KEY')
WASABI_SECRET_ACCESS_KEY = os.getenv('WASABI_SECRET_KEY')



def combine_and_clean_kw_list(site):
    """Combine all the keywords into one clean list and remove duplicates."""
    kw_urls = []
    for i in site['csv_file']:
        kw_urls.append(i['url'])
    df = pd.concat([pd.read_csv(f) for f in kw_urls])
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
    combined_csv = df['Keyword'].str.title()
    # save to csv
    combined_csv.to_csv(
        f"{os.getcwd()}/kw_lists/{site['Keyword Lists'][0]}.csv", index=False)


def send_article_to_spin_rewriter(keyword):
    article_to_spin = f"./new_articles/{keyword}.txt"
    spin_article(article_to_spin, keyword)
    return


def create_hugo_config(domain, dst_dir, offer_link, monetization='302 Redirect'):

    with open(f'{HUGO_TEMPLATE_DIR}/config/_default/config.yaml', 'r') as yaml_file:
        docs = yaml.load(yaml_file, Loader=yaml.FullLoader)
        docs['params']['label']['text'] = f'Welcome to {domain}'
        docs['title'] = domain
        docs['params']['title'] = domain
        docs['params']['description'] = domain
        with open(f'{dst_dir}/config/_default/config.yaml', 'w') as yaml_file:
            docs = yaml.dump(docs, yaml_file)
    offer_link = f"{offer_link}/{domain.replace('.', '')}"
    with open(f'{dst_dir}/content/privacy.html', 'r') as privacy_file:
        content = privacy_file.read()
        new_content = content.replace('{{ domain }}', domain)
    with open(f'{dst_dir}/content/privacy.html', 'w') as privacy_file:
        privacy_file.write(new_content)
    if monetization == '302 Redirect':
        with open(f'{os.getcwd()}/monetization_scripts/redirScript.js', 'r') as redir_script:
            content = redir_script.read()
            new_content = content.replace('{{ offer_link }}', offer_link)
            with open(f'{dst_dir}/static/js/custom.js', 'w') as js_file:
                js_file.write(new_content)

    return


def create_hugo_directory(domain_name):
    new_dir = f'{HUGO_BUILD_PATH}/campaigns/{domain_name}'
    logging.info(f'{os.path.join(current_working_dir, new_dir)}')
    if os.path.exists(new_dir):
        logging.info("removing existing directory")
        shutil.rmtree(new_dir)
    shutil.copytree(HUGO_TEMPLATE_DIR, new_dir)
    return new_dir

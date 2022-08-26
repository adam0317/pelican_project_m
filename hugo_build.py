# from cloudflare import add_site_to_cloudflare, add_dns_to_cloudflare
# import sthree
import csv
import os
import subprocess
from dotenv import load_dotenv
from spin_rw import spin_article
from datetime import datetime
from air_table import get_ready_to_build_records,  update_record
import article_forge
# from build_pages import multi_thread_posts, add_base_pages
import pandas as pd
import ssl
import shutil
from ruamel.yaml import YAML
ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
yaml = YAML()
current_working_dir = os.getcwd()
HUGO_BUILD_PATH = f"{os.getcwd()}/hugo_build_folder"
STAGING_PATH =  os.getenv('STAGING_PATH', '../staging')
HUGO_TEMPLATE_DIR = f'{os.path.join(current_working_dir, "hugo_template_site")}'

def send_article_to_spin_rewriter(keyword):
    article_to_spin = f"./new_articles/{keyword}.txt"
    spin_article(article_to_spin, keyword)
    return

def create_hugo_directory(domain_name):
    new_dir = f'{HUGO_BUILD_PATH}/campaigns/{domain_name}/'
    print(f'{os.path.join(current_working_dir, new_dir)}')
    if os.path.exists(new_dir):
        print("removing existing directory")
        shutil.rmtree(new_dir)
    shutil.copytree(HUGO_TEMPLATE_DIR, new_dir)
    return new_dir


def main():  # sourcery no-metrics

    sites = get_ready_to_build_records()

    for record in sites:
        site = record['fields']
        start_date = site['start_date']
        print(site)
  
        kw_list_exists = False
        for i in site['Keyword Lists']:
            kw_list_exists = os.path.exists(f'{os.getcwd()}/kw_lists/{i}.csv')
            if kw_list_exists:
                break
        if not kw_list_exists:
            print('No KW List Found')
            df = pd.read_csv(f"{site['csv_file'][0]['url']}")
            df.to_csv(f"{os.getcwd()}/kw_lists/{site['csv_file'][0]['filename']}", index=False)
        kw_list_path = f"{os.getcwd()}/kw_lists/{site['csv_file'][0]['filename']}"
        print(f"Starting Full Build {site['Bucket Name']}")
        if 'Test' not in site['Status']:
            update_record(record['id'], {'Status': 'In progress'})
        # continue

        # article_exists = os.path.exists(
        #     f"{os.getcwd()}/new_articles/{site['Article'][0]}.txt")
        # if not article_exists:
        #     print('No Article found Found')
        #     # Get an article from article_forge

        #     continue
        spun_article_dir = f"{os.getcwd()}/spun_articles/{site['Article'][0].lower()}"
 
        if not os.path.exists(spun_article_dir):
            print('No Article Directory Found')
            # Get an article from article_forge

            continue
        elif len(os.listdir(spun_article_dir)) == 0:
            print('No Article Found')
            continue

        
        build_dir = create_hugo_directory(site['Base Domain'])
        print(build_dir)
        create_hugo_config(site['Base Domain'], build_dir, site['offer_link'][0])
        subprocess.Popen(f"php spintax.php {kw_list_path} {spun_article_dir} {build_dir}/content/posts {start_date}", shell=True).wait()

        # DNS management
        # Article Forge Integration

        # Bash script to build hugo site
        # Move public folder to a deployment staging path
        # Zip site and upload to backup s3 bucket 
        return
 

        # update_record(record['id'], {'Status': 'Ready To Deploy'})
def create_hugo_config(domain, dst_dir, offer_link):
    
    yaml_file_dict = {
        'baseURL': ''
        , 'menu': {'main': 
                        [{'identifier': 'contact'
                        , 'name': 'contact'
                        , 'url': 'contact/'
                        , 'weight': 10}
                        , {'identifier': 'disclaimer'
                        , 'name': 'disclaimer'
                        , 'url': 'disclaimer/'
                        , 'weight': 20}
                        , {'identifier': 'privacy'
                        , 'name': 'privacy'
                        , 'url': 'privacy/'
                        , 'weight': 30}
                        , {'identifier': 'sitemap'
                        , 'name': 'sitemap'
                        , 'url': '/sitemap.xml'
                        , 'weight': 40}]
        
        }
        , 'title': domain
        , 'paginate': 50
        , 'theme': 'PaperMod'
        , 'enableRobotsTXT': True
        , 'buildDrafts': False
        , 'buildFuture': False
        , 'buildExpired': False
        , 'minify': {'disableXML': True
        , 'minifyOutput': True}
        , 'params': {'hideFooter': True, 'env': 'production', 'title': domain
        # , 'umami': domain.uuid
        # , 'umamiUrl': 'https://umami-vercel-chi.vercel.app/umami.js'
        , 'custom_js': ['/js/custom.js']
        , 'description': domain
        , 'DateFormat': 'January 2, 2006'
        , 'defaultTheme': 'auto'
        , 'disableThemeToggle': False
        , 'ShowReadingTime': True
        , 'ShowShareButtons': True
        , 'ShowPostNavLinks': True
        , 'ShowBreadCrumbs': True
        , 'ShowCodeCopyButtons': False
        , 'ShowWordCount': True
        , 'ShowRssButtonInSectionTermList': True
        , 'UseHugoToc': True
        , 'disableSpecial1stPost': False
        , 'disableScrollToTop': False
        , 'comments': False
        , 'hidemeta': False
        , 'hideSummary': False
        , 'showtoc': False
        , 'tocopen': False
        , 'label': {'text': f'Welcome to {domain}'
        , 'icon': '/apple-touch-icon.png'
        , 'iconHeight': 35}
        , 'cover': {'hidden': True
        , 'hiddenInList': True
        , 'hiddenInSingle': True}
        
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

if __name__ == "__main__":
    main()
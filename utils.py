import pandas as pd
import os


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

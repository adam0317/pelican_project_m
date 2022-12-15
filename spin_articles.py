import spintax
import os
import pandas as pd
import random


def spin_articles(csv_path, article_dir, article_dst, num_posts, start_date):
    if not os.path.exists(article_dst):
        os.makedirs(article_dst)
    df = pd.read_csv(csv_path)
    for index, row in df.iterrows():
        if int(num_posts) > 0 and index >= int(num_posts):
            break
        # read all articles into a list
        articles = []
        for file in os.listdir(article_dir):
            if file.endswith(".txt"):
                with open(f'{article_dir}/{file}', 'r') as f:
                    articles.append(f.read())

        content = spintax.spin(random.choice(articles))
        with open(f'{article_dst}/content/posts/{row["Keyword"].strip()}.md', 'w') as f:
            f.write(f"---")
            f.write(f"title: \"{row['Keyword']}\"")
            f.write(f"date: {start_date}")
            f.write(f"draft: false")
            f.write(f"keywords: \"[{row['Keyword']}]\"")
            f.write(f"---")
            f.write(f"{content}")


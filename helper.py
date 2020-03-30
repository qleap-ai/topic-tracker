import json
from random import random


def load(file):
    with open(file, encoding='utf8') as json_file:
        articles = json.load(json_file)
    return articles


def trace():
    arts = load("/Users/laemmel/tmp/news_mwes/stripped_articles.json")
    idx = 0
    for art in arts:
        if art['id'] == '1212736627178704896':
            a1 = arts[idx - 1]
            a2 = arts[idx + 1]
            print(art)
        idx += 1
        # if 'west virginia' in art['text'].lower():
        #     print(art)


#

def strip():
    file1 = "/Users/laemmel/tmp/news_mwes/articles_articles-2019-12-31_00_00_01-2020-02-29_00_00_01.json"
    articles = load(file1)

    print(articles.keys())
    art_list = articles['articles']

    file2 = "/Users/laemmel/tmp/news_mwes/articles_articles-2020-03-01_00_00_01-2020-03-29_19_33_32.289736.json"
    articles = load(file2)
    art_list.extend(articles['articles'])
    print(len(art_list))
    ids = set()
    clean_list = []
    for art in art_list:
        if 'text' not in art.keys():
            continue
        r = random()
        if r > 0.1:
            continue

        if art['id'] in ids:
            continue
        ids.add(art['id'])
        clean_list.append(art)
    print(len(clean_list))

    tmp_file = "/Users/laemmel/tmp/news_mwes/stripped_articles.json"
    with open(tmp_file, "w") as tmp:
        json.dump(clean_list, tmp)


trace()

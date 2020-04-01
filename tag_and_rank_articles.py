from datetime import datetime

import load_mwe_model
from article_loader import ArticleLoader
from load_mwe_model import load
from quickmatch import quick_match
import networkx as nx
import time


def tag(art, mwes):
    tags = {}
    art['tags'] = tags
    art['links'] = []
    tag_sum = 0
    for k in mwes.keys():
        text = art['title'] + " " + art['text']
        my_mwes, score = quick_match(text, mwes[k])
        links = [(x, my_mwes[x][0] * my_mwes[x][1]) for x in my_mwes.keys()]
        art['links'].extend(links)
        # todo cosine instead of sum?
        if score > 1.5:
            tags[k] = 1
            tag_sum += 1
        else:
            tags[k] = 0


def rank_arts(arts):
    art_dict = {}
    G = nx.MultiGraph()
    for art in arts:
        if len(art['links']) == 0:
            continue
        art_dict[art['id']] = art
        from_node = art['id']
        for ll in art['links']:
            k = ll[0]
            w = ll[1]
            to_node = k
            G.add_edge(from_node, to_node, weight=w)

    pr = nx.pagerank_numpy(G, alpha=0.9, weight='weight')
    for k in pr.keys():
        if k in art_dict.keys():
            art = art_dict[k]
            art['rank'] = pr[k]
            # print(pr[k])
    arts = list(filter(lambda a: 'rank' in a.keys(), arts))
    arts.sort(key=lambda i: -i['rank'])
    return arts


def compute_tags_and_rank(fr, to):
    al = ArticleLoader()
    start_time = time.time()
    arts = al.load_articles(fr, to)
    print("--- %s seconds ---" % (time.time() - start_time))
    mwes = load()
    for art in arts:
        tag(art, mwes)

    arts = rank_arts(arts)
    topics = list(load_mwe_model.topics)
    topics.append("Other")
    topic_cnt_dict = {}
    for t in topics:
        topic_cnt_dict[t] = 0
    for art in arts:
        tagged = 0
        for k in art['tags']:
            if art['tags'][k] > 0:
                topic_cnt_dict[k] += 1
                tagged += 1
        if tagged == 0:
            topic_cnt_dict['Other'] += 1


    from_date = str(datetime.fromtimestamp(fr).strftime('%Y-%m-%d %H:%M'))
    to_date = str(datetime.fromtimestamp(to).strftime('%Y-%m-%d %H:%M'))
    stripped = [{'title': art['title'], 'url': art['url'], 'handle': art['handle'], 'tags': art['tags'],
                 'date': datetime.fromtimestamp(art['time_stamp']).strftime('%Y-%m-%d %H:%M'), 'rank': art['rank']} for
                art in
                arts]
    tagged_articles = {'from_date': from_date, 'to_date': to_date, 'from_ts': fr, 'to_ts': to, 'articles': stripped,'topic_distr':topic_cnt_dict}
    return tagged_articles
    # pass


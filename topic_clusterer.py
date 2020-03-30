# mwes=
import json
from datetime import datetime
from functools import reduce

import create_mwe_model
import load_mwe_model
from article_loader import ArticleLoader
from quickmatch import quick_match
import time
import mwe_extractor
import networkx as nx
from networkx.algorithms import community


def compute_clusters(articles, model):
    clusters = {}

    for art in articles:
        my_clusters = {}
        for k in model:
            my_res, score = quick_match(art['text'], model[k])
            if score > 2:
                my_clusters[k] = {'mwes': my_res, 'k': k}

        if len(my_clusters) == 0:
            continue
        if len(my_clusters) > 1:
            max_w = 0
            max_k = None
            for kk in my_clusters.keys():
                my_mwes = my_clusters[kk]['mwes']
                weighted = [x[0] * x[1] for x in my_mwes.values()]
                w = reduce(lambda x, y: x + y, weighted)
                if w > max_w:
                    max_w = w
                    max_k = kk
            my_clusters = {max_k: my_clusters[max_k]}
        k = next(iter(my_clusters))
        if k in clusters.keys():
            clusters[k].append({'mwes': my_clusters[k]['mwes'], 'article': art})
        else:
            clusters[k] = [{'mwes': my_clusters[k]['mwes'], 'article': art}]
        # else:

    return clusters


def compute_cluster_mwes(base_clusters, neg_mwe):
    mwes = {}
    for k in base_clusters.keys():
        arts = [art['article'] for art in base_clusters[k]]
        my_mwes = mwe_extractor.extract_mwes(arts)
        mwes[k] = my_mwes - neg_mwe

    filtered_mwes = {}
    for k in mwes.keys():
        k_mwes = mwes[k]
        for l in mwes.keys():
            if k == l:
                continue
            k_mwes = k_mwes - mwes[l]
        filtered_mwes[k] = k_mwes
    return filtered_mwes


# #for debugging
# def draw_graph(G):
#     import matplotlib.pyplot as plt
#     from itertools import cycle
#     cycol = cycle('bgrcmk')
#
#     communities_generator = community.girvan_newman(G)
#     top_level_communities = next(communities_generator)
#     top_level_communities = next(communities_generator)
#
#     pos = nx.spring_layout(G)  # positions for all nodes
#     # nx.draw_networkx_nodes(G, pos, nodelist=G.nodes, node_color='r', node_size=50)
#     idx = 0
#     for i in range(0, len(top_level_communities)):
#         nx.draw_networkx_nodes(G, pos, nodelist=list(top_level_communities[i]), node_color=next(cycol), node_size=50)
#
#     # edges
#     el = [(u, v) for (u, v, d) in G.edges(data=True)]
#     nx.draw_networkx_edges(G, pos, edgelist=el,
#                            width=5)
#
#     # labels
#     nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
#     plt.axis('off')
#     plt.show()


def rank_cluster(cluster):
    G = nx.Graph()
    url_art = {}
    for article in cluster:
        art = article['article']
        url_art[art['url']] = art
        to_node = art['url']
        mwes = article['mwes']
        for mwe in mwes:
            fr_node = mwe
            w = mwes[mwe][0]*mwes[mwe][1]
            G.add_edge(fr_node, to_node, weight=w)
            G.add_edge(to_node, fr_node, weight=w)

    # draw_graph(G)
    communities_generator = community.girvan_newman(G)
    top_level_communities = next(communities_generator)
    # top_level_communities = next(communities_generator)
    idx = 0
    for s in top_level_communities:
        sub = G.subgraph(s)
        pr = nx.pagerank_numpy(sub, alpha=0.9, weight='weight')
        for k in pr.keys():
            v = pr[k]
            if k in url_art.keys():
                art = url_art[k]
                art['rank'] = v
                art['group'] = idx
        idx += 1


def rank_clusters(clusters):
    for k in clusters.keys():
        rank_cluster(clusters[k])


def compute_ranked_clusters(fr, to):
    # base_model, pre_filter = create_mwe_model.build_model()
    base_model, pre_filter = load_mwe_model.load()
    loader = ArticleLoader()
    articles = loader.load_articles(fr, to)

    # apply base filter
    pre_filter_articles = []
    neg_corp = []
    for art in articles:
        match, score = quick_match(art['text'], pre_filter)
        if score > 2:
            pre_filter_articles.append(art)
        else:
            neg_corp.append(art)

    # neg corp mwe
    neg_mwe = mwe_extractor.extract_mwes(neg_corp)

    # seed term iteration
    base_clusters = compute_clusters(articles, base_model)
    rank_clusters(base_clusters)
    return base_clusters

    #
    # cluster_mwes = compute_cluster_mwes(base_clusters, neg_mwe)
    #
    # for k in cluster_mwes.keys():
    #     base_model[k].update(cluster_mwes[k])
    #
    # # 2nd seed term iteration
    # clusters = compute_clusters(articles, base_model)
    # rank_clusters(clusters)
    # # print(clusters)
    # return clusters


def compute_topic_clusters(fr, to):
    ranked_cluster = compute_ranked_clusters(fr, to)

    clusters = {'topics': {}}

    for topic in ranked_cluster.keys():
        my_clusters = ranked_cluster[topic]
        groups = {}
        for e in my_clusters:
            if not 'group' in e['article'].keys():
                continue
            g = e['article']['group']
            if g in groups:
                groups[g].append(e['article'])
            else:
                groups[g] = [e['article']]
            newlist = sorted(groups[g], key=lambda k: k['rank'])
            groups[g] = newlist
        # print(groups)
        res = []
        while len(groups) > 0 and len(res) < 5:
            for k in groups:
                ll = groups[k]
                if len(ll) > 0:
                    art = ll.pop()
                    if 'text' in art.keys():
                        art.pop('text')
                        res.append(art)
                else:
                    groups.pop(k)
                    break
        print(res)
        from_date = str(datetime.fromtimestamp(fr))
        to_date = str(datetime.fromtimestamp(to))
        clusters['topics'][topic] = res
        clusters['from_date'] = from_date
        clusters['to_date'] = to_date
        clusters['from_ts'] = fr
        clusters['to_ts'] = to
    return clusters

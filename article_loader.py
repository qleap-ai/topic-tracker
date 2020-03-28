from fuzzywuzzy import fuzz
from firebase_admin import firestore
import nltk

class ArticleLoader:
    def __init__(self):
        self.fire_db = firestore.Client()
        self.handles = set()


    # loads all articles for a given collection for above defined time period
    def get_articles(self, col, fr, to):
        art_stream = self.fire_db.collection('news').document('articles') \
            .collection(col).where("time_stamp", ">=", fr).where("time_stamp", "<=", to).stream()
        arts = []
        for art_ref in art_stream:
            art = art_ref.to_dict()
            arts.append(art)
        if len(arts) > 0:
            self.handles.add(col)
        return arts


    # iterates over the collections to load the articles
    def load_articles(self, fr, to):
        colls = self.fire_db.collection('news').document('articles').collections()
        ll = list(colls)
        all_articles = []
        for col in ll:
            my_articles = self.get_articles(col.id, fr, to)
            all_articles.extend(my_articles)
        all_articles = self.rm_inconsitent(all_articles)
        all_articles = self.filter_unique(all_articles)
        return all_articles


    def filter_unique(self, articles):
        unique = []
        unique.append(articles[0])
        for j in range(1, len(articles)):
            cand = articles[j]
            word_list = nltk.word_tokenize(cand['title'].replace("-", " "))
            t1 = " ".join([word.lower() for word in word_list if word.isalpha()])
            accept = True
            for art in unique:
                word_list = nltk.word_tokenize(art['title'].replace("-", " "))
                t2 = " ".join([word.lower() for word in word_list if word.isalpha()])
                sim = fuzz.token_sort_ratio(t1, t2)
                if sim > 90:
                    accept = False
                    break
            if accept:
                unique.append(cand)
        return unique


    def rm_inconsitent(self, articles):
        ret = []
        for art in articles:
            if 'title' in art.keys() and len(art['title']) > 0 and 'text' in art.keys():
                ret.append(art)

        return ret




import networkx as nx

from nltk.tokenize.punkt import PunktSentenceTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import os
import re

QUOTES = re.compile(r'[’‘“”]')

class TextRank:
    def __init__(self, path):
        document = path
        if os.path.exists(path):
            with open(path, "r") as file:
                document = file.read().replace('\n', ' ')

        document = QUOTES.sub('', document)

        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        sentence_tokenizer = PunktSentenceTokenizer()

        self.sentences = sentence_tokenizer.tokenize(document)
        bow_matrix = tfidf_vectorizer.fit_transform(self.sentences)
        self.tfidf_features = tfidf_vectorizer.get_feature_names()

        sentence_similarity_matrix = bow_matrix * bow_matrix.T
        word_similarity_matrix = bow_matrix.T * bow_matrix

        self.sentence_nx_graph = nx.from_scipy_sparse_matrix(sentence_similarity_matrix)
        self.word_nx_graph = nx.from_scipy_sparse_matrix(word_similarity_matrix)


    def get_sentence(self, index):
        return self.sentences[index]

    def get_word(self, index):
        return self.tfidf_features[index]

    def plot_sentence_graph(self):
        self.plot_graph(self.sentence_nx_graph)

    def plot_word_graph(self):
        self.plot_graph(self.word_nx_graph)

    def plot_graph(self, graph):
        nx.draw(graph, with_labels=True)
        plt.show()
        plt.close()


    def key_sentences(self, topn=None):
        scores = nx.pagerank(self.sentence_nx_graph)
        return sorted(((scores[i], s) for i, s in enumerate(self.sentences)),
                      reverse=True)[:topn]

    def keywords(self, topn=None):
        scores = nx.pagerank(self.word_nx_graph)
        return sorted(((scores[i], s) for i, s in enumerate(self.tfidf_features)),
                      reverse=True)[:topn]
from py2neo import Graph
import re, string
from nltk.corpus import stopwords
import nltk

nltk.download("stopwords")

PUNCTUATION = re.compile('[%s’‘“”]' % re.escape(string.punctuation))

# define some parameterized Cypher queries

# For data insertion
INSERT_QUERY = '''
    FOREACH (t IN {wordPairs} | 
        MERGE (w0:Word {word: t[0]})
            ON CREATE SET w0.count = 1
            ON MATCH SET w0.count = w0.count + 1
        MERGE (w1:Word {word: t[1]})
            ON CREATE SET w1.count = 1
            ON MATCH SET w1.count = w1.count + 1
        MERGE (w0)-[r:NEXT_WORD]->(w1)
            ON CREATE SET r.count = 1
            ON MATCH SET r.count = r.count + 1
        )
'''

# get the set of words that appear to the left of a specified word in the text corpus
LEFT1_QUERY = '''
    MATCH (s:Word {word: {word}})
    MATCH (w:Word)-[:NEXT_WORD]->(s)
    RETURN w.word as word
'''

# get the set of words that appear to the right of a specified word in the text corpus
RIGHT1_QUERY = '''
    MATCH (s:Word {word: {word}})
    MATCH (w:Word)<-[:NEXT_WORD]-(s)
    RETURN w.word as word
'''

PARADIGMATIC_RELATIONS_QUERY = '''
    // Create paradigmatic relations between words
    // From http://www.lyonwj.com/2015/06/16/nlp-with-neo4j/
    MATCH (s:Word)
    // Get right1, left1
    MATCH (w:Word)-[:NEXT_WORD]->(s)
    WITH collect(DISTINCT w.word) as left1, s
    MATCH (w:Word)<-[:NEXT_WORD]-(s)
    WITH left1, s, collect(DISTINCT w.word) as right1
    // Match every other word
    MATCH (o:Word) WHERE NOT s = o
    WITH left1, right1, s, o
    // Get other right, other left1
    MATCH (w:Word)-[:NEXT_WORD]->(o)
    WITH collect(DISTINCT w.word) as left1_o, s, o, right1, left1
    MATCH (w:Word)<-[:NEXT_WORD]-(o)
    WITH left1_o, s, o, right1, left1, collect(DISTINCT w.word) as right1_o
    // compute right1 union, intersect
    WITH FILTER(x IN right1 WHERE x IN right1_o) as r1_intersect,
      (right1 + right1_o) AS r1_union, s, o, right1, left1, right1_o, left1_o
    // compute left1 union, intersect
    WITH FILTER(x IN left1 WHERE x IN left1_o) as l1_intersect,
      (left1 + left1_o) AS l1_union, r1_intersect, r1_union, s, o
    WITH DISTINCT r1_union as r1_union, l1_union as l1_union, r1_intersect, l1_intersect, s, o
    WITH 1.0*length(r1_intersect) / length(r1_union) as r1_jaccard,
      1.0*length(l1_intersect) / length(l1_union) as l1_jaccard,
      s, o
    WITH s, o, r1_jaccard, l1_jaccard, r1_jaccard + l1_jaccard as sim
    CREATE UNIQUE (s)-[r:RELATED_TO]->(o) SET r.paradig = sim;
'''

class NeoGraph():
    def __init__(self, filepath=None, strip_stopwords=True):
        # connect to Neo4j instance using py2neo - default running locally
        self._graphdb = Graph('http://neo4j:pass@localhost:7474/db/data')
        if filepath:
            self.load_file(filepath, strip_stopwords)

    def sentence_to_array(self, sentence, strip_stopwords=True):
        """
        # convert a sentence string into a list of lists of adjacent word pairs
        # sentence_to_array("Hi there, Bob!") = [["hi", "there"], ["there", "bob"]]
        :param sentence:  sentence string
        :param strip_stopwords: True if stopwords should be removed
        :return: string array
        """
        sentence = sentence.lower()
        sentence = sentence.strip()
        sentence = PUNCTUATION.sub('', sentence)
        if strip_stopwords:
            word_array = [word for word in sentence.split() if word not in stopwords.words('english')]
        else:
            word_array = sentence.split()
        tuple_list = []
        for i, word in enumerate(word_array):
            if i + 1 == len(word_array):
                break
            tuple_list.append([word, word_array[i + 1]])
        return tuple_list

    def load_file(self, filepath, strip_stopwords=True):
        tx = self._graphdb.begin()
        with open(filepath, "r") as f:
            count = 0
            for l in f:
                params = {'wordPairs': self.sentence_to_array(l, strip_stopwords)}
                tx.run(INSERT_QUERY, params)
                tx.process()
                count += 1
                if count > 300:
                    tx.commit()
                    tx = self._graphdb.begin()
                    count = 0
        f.close()
        tx.commit()

    def left1(self, word):
        """ 
        :param word: word string
        :return: a set of all words that appear to the left of `word`
        """
        params = {
            'word': word.lower()
        }
        tx = self._graphdb.begin()
        results = tx.run(LEFT1_QUERY, params)
        tx.commit()
        words = []
        for result in results:
            for line in result:
                words.append(line)
        return set(words)

    def right1(self, word):
        """
        :param word: word string
        :return: a set of all words that appear to the right of `word`
        """
        params = {
            'word': word.lower()
        }
        tx = self._graphdb.begin()
        results = tx.run(RIGHT1_QUERY, params)
        tx.commit()
        words = []
        for result in results:
            for line in result:
                words.append(line)
        return set(words)

    def add_paradigmatic_relations(self):
        tx = self._graphdb.begin()
        tx.run(PARADIGMATIC_RELATIONS_QUERY)
        tx.commit()

    def jaccard(self, a, b):
        """
        :param a: first word
        :param b: second word
        :return: jaccard distance between word a and word b
        """
        intersection_len = len(a.intersection(b))
        union_len = len(a.union(b))
        return intersection_len / union_len

    def paradigmatic_similarity(self, w1, w2):
        """
        we define paradigmatic similarity as the average of the Jaccard coefficents of the `left1` and `right1` sets
        :param w1: first word
        :param w2: second word
        :return: paradigmatic similarity score
        """
        return (self.jaccard(self.left1(w1), self.left1(w2)) + self.jaccard(self.right1(w1), self.right1(w2))) / 2.0

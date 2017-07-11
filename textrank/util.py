from collections import Counter


def bag_of_words(sentence):
    return Counter(word.lower().strip('.,') for word in sentence.split(' '))


def doc_bag_of_words(sentences):
    if len(sentences) == 0:
        return Counter()
    else:
        sentence = sentences[0]
    return bag_of_words(sentence) + doc_bag_of_words(sentences[1:])
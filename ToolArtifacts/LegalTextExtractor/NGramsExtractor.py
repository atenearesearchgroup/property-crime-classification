import spacy
import os
import sys
from dataUtils.SentencesLoader import load_sentences_file_by_file
from ConfigurationParams import ConfigurationParams
import string
import copy

def valid_token(token):
    return not all([x in string.punctuation for x in token.text])

def ngrams_builder(doc, length):
    ngrams = []
    current_ngram = []
    current_pos = 0
    while len(current_ngram)<length and current_pos < len(doc):
        if valid_token(doc[current_pos]):
            current_ngram.append(current_pos)
        current_pos+=1
    ngrams.append(copy.copy(current_ngram))
    while current_pos < len(doc):
        if (valid_token(doc[current_pos])):
            current_ngram = copy.copy(current_ngram[1:])
            current_ngram.append(current_pos)
            ngrams.append(copy.copy(current_ngram))
        current_pos+=1
    return ngrams

if __name__ == '__main__':
    sentences = load_sentences_file_by_file(sys.argv[1])
    nlp = spacy.load(ConfigurationParams.MODEL)
    global_ngrams = {}
    for filename in sentences:
        print (f'processing {filename}...')
        local_ngrams = {}
        for s in sentences[filename]:
            doc = nlp(s)
            for ngram in ngrams_builder(doc, int (sys.argv[2])):
                text = " ".join([doc[x].text for x in ngram])
                if text not in local_ngrams:
                    local_ngrams[text] = 0
                if text not in global_ngrams:
                    global_ngrams[text] = 0
                local_ngrams[text] += 1
                global_ngrams[text] += 1
        with open(filename+"_ngrams_"+sys.argv[2], "w") as out:
            sort_orders = sorted(local_ngrams.items(), key=lambda x:x[1], reverse=True)
            for i in sort_orders:
                if (i[1] > 1):
                    out.write(f'{i[0]} -- {i[1]}\n')

    with open("docs_global_ngrams"+sys.argv[2], "w") as out:
        sort_orders = sorted(global_ngrams.items(), key=lambda x: x[1], reverse=True)
        for i in sort_orders:
            if (i[1] > 1):
                out.write(f'{i[0]} -- {i[1]}\n')
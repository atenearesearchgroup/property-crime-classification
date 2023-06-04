import spacy
import os
import sys
from dataUtils.SentencesLoader import load_sentences_file_by_file
from ConfigurationParams import ConfigurationParams
import string

def retrieve_mays_spans (doc):
    spans = []
    span_begin = -1
    span_end = -1
    for x in enumerate(doc):
        if span_begin == -1:
            if all([x.isupper() or x in string.punctuation for x in x[1].text]) \
                    and (any([x.isupper() for x in x[1].text])):
                span_begin = x[0]
                span_end = x[0]
        else:
            if not ( all([x.isupper() or x in string.punctuation for x in x[1].text])
                    and (any ([x.isupper() for x in x[1].text])) ):
                spans.append((span_begin, span_end))
                span_begin = -1
            else:
                span_end = x[0]
    if span_begin != -1:
        spans.append((span_begin, span_end))
    return spans

if __name__ == '__main__':
    sentences = load_sentences_file_by_file(sys.argv[1])
    nlp = spacy.load(ConfigurationParams.MODEL)
    global_mays = {}
    for filename in sentences:
        print (f'processing {filename}...')
        local_mays = {}
        for s in sentences[filename]:
            doc = nlp(s)
            for mays_span in retrieve_mays_spans(doc):
                text = " ".join([x.text for x in doc[mays_span[0]:mays_span[1]]])
                if text not in local_mays:
                    local_mays[text] = 0
                if text not in global_mays:
                    global_mays[text] = 0
                local_mays[text] += 1
                global_mays[text] += 1
        with open(filename+"_sections", "w") as out:
            sort_orders = sorted(local_mays.items(), key=lambda x:x[1], reverse=True)
            for i in sort_orders:
                out.write(f'{i[0]} -- {i[1]}\n')

    with open("docs_global_sections", "w") as out:
        sort_orders = sorted(global_mays.items(), key=lambda x: x[1], reverse=True)
        for i in sort_orders:
            out.write(f'{i[0]} -- {i[1]}\n')
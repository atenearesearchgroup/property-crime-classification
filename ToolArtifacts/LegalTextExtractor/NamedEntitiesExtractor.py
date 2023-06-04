import spacy
import os
import sys
from dataUtils.SentencesLoader import load_sentences_file_by_file
from ConfigurationParams import ConfigurationParams

if __name__ == '__main__':
    sentences = load_sentences_file_by_file(sys.argv[1])
    nlp = spacy.load(ConfigurationParams.MODEL)
    global_nes = {}
    for filename in sentences:
        print (f'processing {filename}...')
        local_nes = {}
        for s in sentences[filename]:
            doc = nlp(s)
            for ne in doc.ents:
                text = ne.text
                if text not in local_nes:
                    local_nes[text] = {'labels': {}, 'count':0}
                if text not in global_nes:
                    global_nes[text] = {'labels':{}, 'count': 0}

                if ne.label_ not in local_nes[text]['labels']:
                    local_nes[text]['labels'][ne.label_] = 0
                if ne.label_ not in global_nes[text]['labels']:
                    global_nes[text]['labels'][ne.label_] = 0

                local_nes[text]['count'] +=1
                global_nes[text]['count'] += 1
                local_nes[text]['labels'][ne.label_] += 1
                global_nes[text]['labels'][ne.label_] += 1

        with open(filename+"_nes.txt", "w") as out:
            sort_orders = sorted(local_nes.items(), key=lambda x:x[1]['count'], reverse=True)
            for i in sort_orders:
                out.write(f'{i[0]} -- {i[1]}\n')

    with open("docs_global_nes.txt", "w") as out:
        sort_orders = sorted(global_nes.items(), key=lambda x: x[1]['count'], reverse=True)
        for i in sort_orders:
            out.write(f'{i[0]} -- {i[1]}\n')
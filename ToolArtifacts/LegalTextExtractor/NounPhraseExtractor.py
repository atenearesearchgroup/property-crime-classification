import spacy
import os
import sys
from dataUtils.SentencesLoader import load_sentences_file_by_file
from ConfigurationParams import ConfigurationParams



if __name__ == '__main__':
    sentences = load_sentences_file_by_file(sys.argv[1])
    nlp = spacy.load(ConfigurationParams.MODEL)
    global_nounphrases = {}
    for filename in sentences:
        print (f'processing {filename}...')
        local_nounphrases = {}
        for s in sentences[filename]:
            doc = nlp(s)
            for noun_phrase in doc.noun_chunks:
                text = noun_phrase.text
                if text not in local_nounphrases:
                    local_nounphrases[text] = 0
                if text not in global_nounphrases:
                    global_nounphrases[text] = 0
                local_nounphrases[text] += 1
                global_nounphrases[text] += 1
        with open(filename+"_nounphrases", "w") as out:
            sort_orders = sorted(local_nounphrases.items(), key=lambda x:x[1], reverse=True)
            for i in sort_orders:
                out.write(f'{i[0]} -- {i[1]}\n')

    with open("docs_global_nounphrases", "w") as out:
        sort_orders = sorted(global_nounphrases.items(), key=lambda x: x[1], reverse=True)
        for i in sort_orders:
            out.write(f'{i[0]} -- {i[1]}\n')
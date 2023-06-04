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
            mays_spans = retrieve_mays_spans(doc)
            if len(mays_spans) != 0:
                template = ['####****']*len(doc)
                template_ner = ['####****']*len(doc)
                for m_span in mays_spans:
                    template[m_span[0]:m_span[1]] = [x.text for x in doc[m_span[0]:m_span[1]]]
                    template_ner[m_span[0]:m_span[1]] = [x.text for x in doc[m_span[0]:m_span[1]]]
                for ent in doc.ents:
                    template[ent.start:ent.end] = [x.text for x in doc[ent.start:ent.end]]
                    template_ner[ent.start:ent.end] = [ent.label_]*(ent.end-ent.start)
                template = [x for x in template if x != '####****']
                print(f'template: {template}')
                template_ner = [x for x in template_ner if x != '####****']
                print(f'template_ner: {template_ner}')
                text_template = ' '.join(template)
                print(f'text_template: {text_template}')
                text_template_ner = ' '.join(template_ner)
                print(f'text_template_ner: {text_template_ner}')
                if text_template_ner not in local_mays:
                    local_mays[text_template_ner] = {'cnt':0, 'ext':[]}
                if text_template_ner not in global_mays:
                    global_mays[text_template_ner] = {'cnt':0, 'ext': []}
                local_mays[text_template_ner]['cnt'] +=1
                local_mays[text_template_ner]['ext'].append(text_template)
                global_mays[text_template_ner]['cnt'] +=1
                global_mays[text_template_ner]['ext'].append(text_template)
        with open(filename+"_uppPatterns", "w") as out:
            sort_orders = sorted(local_mays.items(), key=lambda x:x[1]['cnt'], reverse=True)
            for i in sort_orders:
                out.write(f'{i[0]} -- {i[1]["cnt"]}\n')
                for x in i[1]['ext']:
                    out.write(f'\t{x}\n')
    with open("docs_global_uppPatterns", "w") as out:
        sort_orders = sorted(global_mays.items(), key=lambda x: x[1]['cnt'], reverse=True)
        for i in sort_orders:
            out.write(f'{i[0]} -- {i[1]["cnt"]}\n')
            for x in i[1]['ext']:
                out.write(f'\t{x}\n')
import spacy
import os
import sys
from dataUtils.SentencesLoader import load_sentences_file_by_file
from ConfigurationParams import ConfigurationParams


DEPS_TO_FOLLOW = ['acl', 'acl: relcl', 'amod', 'appos',
    'compound', 'dep', 'det', 'case', 'fixed', 'flat',
    'list', 'nmod', 'nummod']
POS_TO_PROCESS = ['NOUN', 'PROPN']


def is_idx_part_of_entity(idx,dep_parse):
    # print(f'is_idx: {idx} - {dep_parse[idx]}')
    for i in range(len(dep_parse.ents)):
        # print(f'ent: {dep_parse.ents[i].start} - {dep_parse.ents[i].end} : {[dep_parse[x] for x in range(dep_parse.ents[i].start, dep_parse.ents[i].end)]}')
        if dep_parse.ents[i].start <= idx and idx <= dep_parse.ents[i].end:
            return True
    return False

# if any children decides to return an emtpy list, we will discard that path
def explore_children_recursively (idx, doc):
#     print (f'word {idx} {doc[idx]}')
    aux_it=[c for c in doc[idx].children]
    if (len(aux_it) == 0):
        # we are in a leaf
        if not is_idx_part_of_entity (idx, doc):
            return [idx]
        else:
            return []
    else:
        aux_children = []
        for c in doc[idx].children:
            aux_children.append(explore_children_recursively(c.i, doc))
        aux_result = []
        if (all([len(x) > 0 for x in aux_children])):
            aux_result = []
            for x in aux_children:
                aux_result += x
            aux_result.insert(0, idx)
        return aux_result

def obtain_children_pruning(idx, doc):
    # print ('-----\n')
    # print(f'{idx} .. doc: {doc}\n')
    # print(f'{doc[idx]}\n')
    to_process = [c for c in doc[idx].children if c.dep_ in DEPS_TO_FOLLOW]
    children=[idx]
    for c in to_process:
        children += explore_children_recursively(c.i, doc)
    return sorted(children)

if __name__ == '__main__':
    sentences = load_sentences_file_by_file(sys.argv[1])
    nlp = spacy.load(ConfigurationParams.MODEL)
    global_nounphrases = {}
    for filename in sentences:
        # print (f'processing {filename}...')
        local_nounphrases = {}
        for s in sentences[filename]:
            doc = nlp(s)
            # print(f'{[(x,x.i) for x in doc if x.pos_ in POS_TO_PROCESS]}')
            for noun_head in [x for x in doc if x.pos_ in POS_TO_PROCESS]:
                children = obtain_children_pruning(noun_head.i, doc)
                text = " ".join([doc[x].text for x in children])
                if text not in local_nounphrases:
                    local_nounphrases[text] = 0
                if text not in global_nounphrases:
                    global_nounphrases[text] = 0
                local_nounphrases[text] += 1
                global_nounphrases[text] += 1
        with open(filename+"_noundeps", "w") as out:
            sort_orders = sorted(local_nounphrases.items(), key=lambda x:x[1], reverse=True)
            for i in sort_orders:
                out.write(f'{i[0]} -- {i[1]}\n')

    with open("docs_global_noundeps", "w") as out:
        sort_orders = sorted(global_nounphrases.items(), key=lambda x: x[1], reverse=True)
        for i in sort_orders:
            out.write(f'{i[0]} -- {i[1]}\n')
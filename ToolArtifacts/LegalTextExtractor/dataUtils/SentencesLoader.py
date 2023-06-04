import glob
import os
import sys

FILENAME_EXTENSION='*.txt'

def load_sentences(dir, min_length=3, limit=-1):
    sentences = []
    written = 0
    read = 0
    for filename in glob.glob(os.path.join(dir, FILENAME_EXTENSION)):
        with open(filename, 'r', encoding='UTF-8') as input:
            for line in input.readlines():
                read += 1
                if len(line.rstrip('\n').lstrip('\ufeff')) > min_length:
                    written += 1
                    sentences.append(line.rstrip('\n').lstrip('\ufeff'))
            if (limit != -1 and written>limit):
                print(f'read: {read} not skipped: {written} ')
                return sentences
    print(f'read: {read} not skipped: {written} ')
    return sentences

def load_sentences_file_by_file (dir, min_length=3):
    sentences = {}
    written = 0
    read = 0
    for filename in glob.glob(os.path.join(dir, FILENAME_EXTENSION)):
        sentences[filename] = []
        with open(filename, 'r', encoding='UTF-8') as input:
            for line in input.readlines():
                read += 1
                if len(line.rstrip('\n').lstrip('\ufeff')) > min_length:
                    written += 1
                    sentences[filename].append(line.rstrip('\n').lstrip('\ufeff'))
    print(f'read: {read} not skipped: {written} ')
    return sentences

if __name__ == "__main__":
    sents = load_sentences(sys.argv[1])
    print (f'{len(sents)} sentences in the file')
    print (f'{len([s for s in sents if len(s) > 2])} longer than 1 char ')
    print (f'{[s for s in sents[::100]]}')
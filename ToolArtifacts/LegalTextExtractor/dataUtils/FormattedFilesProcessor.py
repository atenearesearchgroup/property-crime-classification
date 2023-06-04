import os
import sys
import glob

if __name__=="__main__":
    print(os.path.join(sys.argv[1], '*.txt'))
    for filename in glob.glob(os.path.join(sys.argv[1], '*.txt')):
        print(f'processing {filename}...')
        with open(filename, 'r', encoding='UTF-8') as input, open(filename+'-proc.txt', 'w', encoding='UTF-8') as output:
            initial = input.readline()
            if (initial.startswith('Atestado:')):
                output.write(initial)
                for line in input.readlines():
                    if not (line.endswith(initial) or (line.rstrip('\n')=='')):
                        output.write(line)
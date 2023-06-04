from tika import parser
import sys

raw = parser.from_file(sys.argv[1])
print(raw['content'])



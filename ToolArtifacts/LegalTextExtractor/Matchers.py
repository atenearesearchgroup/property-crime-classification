import spacy

PATTERNS_DENUNCIANTE=[
        [{'ORTH': 'DENUNCIANTE'},
           {'OP': '+'},
           {'ENT_TYPE': 'PERSON'}],

]

PATTERNS_DELITOS = [
    [{'LOWER': 'Delito'},
     {'LOWER': 'Leve'},
     {},
     {'LOWER': 'Hurto'}]
]
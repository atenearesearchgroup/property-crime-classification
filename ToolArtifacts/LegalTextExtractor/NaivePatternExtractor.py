import spacy
import os
import sys
from dataUtils.SentencesLoader import load_sentences_file_by_file
from ConfigurationParams import ConfigurationParams
import string
from enum import Enum
import re
import os
import glob


## POSSIBLE MINI_SECTIONS
class ParsingStates(Enum):
    MAIN_SECTION = 0
    DENUNCIANTE_SECTION = 1
    DENUNCIADO_SECTION = 2
    DILIGENCIA_SECTION = 3
    RELACION_OBJETOS_SECTION = 4

## we differentiate the labels of entities from the
## labels of entities even though they share the same annotation space
## for the sake of implementation's simplicity

class CustomOutputLabels:
    PREFIJO_ONTOLOGIA = "<ONT-DELITOS#"
    MARCA_PERTENENCIA = "BelongsTo>"
    MARCA_PERTENENCIA = "IsReferencedIn>"
    MARCA_ES_ROBADO_POR = "IsTheftBy>"
    MARCA_ES_USADO_POR = "IsUsedBy>"
    MARCA_TYPE = "rdf:type owl:NamedIndividual" 
    MARCA_CARACTERISTICA_OFENSA = "hasOffenceCharacteristic>"
    MARCA_ELEMENTO_OFENSA = "OffenceElement>"
    MARCA_ELEMENTO_MOVIBLE = "MovableThing>"
    MARCA_SEPARADOR_COMA = " , "
    MARCA_SEPARADOR_PUNTOYCOMA = " ; "
    
class OutputLabels:
    PREFIJO_ONTOLOGIA = "http://ont#"
    MARCA_DELITO = "delito_contra_patrimonio:"
    MARCA_TYPE = "rdf:type owl:NamedIndividual"
    MARCA_CLASS = "rdf:type owl:Class"
    

class CustomEntityLabels:
    TIPO_DELITO = "TIPO_DELITO"
    DNI = "DNI"
    NUM_SOPORTE = "NUM_SOPORTE"
    COSTE = "COSTE"
    CANTIDAD = "CANTIDAD"
    TICKET = "TICKET"
    DENUNCIANTE  = "DENUNCIANTE"
    COMENTARIO = "COMENTARIO"
    ATESTADO = "ATESTADO"
    OFFENCE_ELEMENT_POSSIBLE_CONTEXT_ROBBERY = "OFFENCE_ELEMENT_POSSIBLE_CONTEXT_ROBBERY"
    OFFENCE_ELEMENT_CONTEXT_ROBBERY = "OFFENCE_ELEMENT_CONTEXT_ROBBERY"
    OFFENCE_ELEMENT_RELACION_OBJETOS = "OFFENCE_ELEMENT_RELACION_OBJETOS"
    OWNER = "COMPANY"
    POSIBLE_OWNER = "POSIBLE_OWNER"
    LOCATION = "LOCATION"
    DOOR_FORCED = "DOOR_FORCED"
    BREAKING = "BREAKING"
    VIOLENCE = "VIOLENCE"
    AGRAVANTE = "AGRAVANTE"
    OFFENCE_ELEMENT = "OFFENCE_ELEMENT"
    PARTE_PERJUDICADA = "PARTE_PERJUDICADA"
    ACCUSED = "ACCUSED"
    SIG_SECCION_DENUNCIADO_SECCION =  "SIG_SECCION_DENUNCIADO_SECCION"
    EL_CORTE_INGLES = "EL_CORTE_INGLES"
    OBJETO_VALORADO = "OBJETO_VALORADO"
    
    
class CustomEntityRelations:    
    STOLEN_BY = "STOLEN_BY"
    OWNED_BY = "OWNED_BY"
    DETENCIONES_ANTERIORES  = "DETENCIONES_ANTERIORES"
    SER = "IS"
    CARACTERISTICA_DE_LA_OFENSA = "CARACTERISTICA_DE_LA_OFENSA"

class SectionLabels:
    RELACION_SECTION = "RELACION_SECTION"
    DENUNCIANTE_SECTION = "DENUNCIANTE_SECTION"
    DENUNCIADO_SECTION = "DENUNCIADO_SECTION"
    DILIGENCIA_START = "DILIGENCIA_START"
    DILIGENCIA_END = "DILIGENCIA_END"
    
class entidad():
    def __init__(self):
        self.palabra = ""    
        self.tipo = ""
        self.relacion = ""
        
class extraccion():
    def __init__(self):
        self.codigo = ""    
        
NEUTRAL_START_RE = re.compile('^--')

#variable de control del proceso
class flags_completed():
    def __init__(self):
        self.NUMERO_ATESTADO_OK = False
        self.OFFENSE_ELEMENT_OK = False
        self.OWNER_OK = False
        self.DOOR_FORCED_OK = False
        self.ACCUSED_OK = False
        self.VIOLENCE_OK = False
        self.BREAKING_OK = False
        
flags = flags_completed()     

def inicializar_flags():
        flags.NUMERO_ATESTADO_OK = False
        flags.OFFENSE_ELEMENT_OK = False
        flags.OWNER_OK = False
        flags.DENUNCIANTE_OK = False
        flags.DOOR_FORCED_OK = False
        flags.ACCUSED_OK = False
        flags.COSTE_OK = False
        flags.RELACION_OBJETOS = False

## Patterns to detect Entities in particular (we will use them as well to detect Sections)
## It's not the cleanest method, but this allow us to give it preference to the entity ruler
## and to have everything tagged in the "entities space"

# note that regex works at token level, so sometimes we will have to check the regular expressions outside
# the entity ruler

# {"label": "NEUTRAL_START", "pattern": [{"TEXT": {"REGEX": "^-- "}}]},

patterns = [
    
            #--- REGLAS DE CARLOS
            
            {"label": CustomEntityLabels.TIPO_DELITO, "pattern":[{"LOWER":"robo"}]},
            {"label": CustomEntityLabels.TIPO_DELITO, "pattern": [{"LOWER": "hurto"}]},
            {"label": CustomEntityLabels.TIPO_DELITO, "pattern": [{"LOWER": "robo"}, {"LOWER":"con"},
                                                    {"LOWER": {"IN": ["violencia", "fuerza", "intimidación", "intimidacion"]}},
                                                 {"LOWER":"o", "OP": "?"},
                                                 {"LOWER":{"IN":["intimidación", "intimidacion"]}, "OP": "?"}]},
            {"label": CustomEntityLabels.TIPO_DELITO, "pattern": [{"LOWER": {"IN": ["sustracción", "sustraccion"]}}]},
            {"label": CustomEntityLabels.TIPO_DELITO, "pattern": [{"LOWER": {"IN": ["receptación", "receptacion"]}}]},

            {"label": SectionLabels.RELACION_SECTION, "pattern":[{"LOWER": {"IN": ["relación", "relacion"]}},
                                                    {"LOWER":"de"}]},
            {"label":  SectionLabels.RELACION_SECTION, "pattern": [{"LOWER": {"IN": ["--relacion", "--relación"]}}]},
            {"label":  SectionLabels.RELACION_SECTION, "pattern": [{"TEXT": {"REGEX": "[Oo][Bb][Jj][Ee][Tt][Oo][Ss]?[:]?"}}]},

            {"label": SectionLabels.DENUNCIANTE_SECTION, "pattern":[{"LOWER": {"IN":  ["denunciante", "denunciantes", "vigilante","vigilantes","manifiesta"]}}]},
            {"label": SectionLabels.DENUNCIANTE_SECTION, "pattern":  
                                          [{"LEMMA": "victima"},{"lOWER": "responde"},{"lOWER": "al"},{"LEMMA": "nombre"},{"lOWER": "de"}]},
           
            
            {"label": SectionLabels.DENUNCIADO_SECTION, "pattern": [{"LOWER": {"IN": ["denunciado", "denunciado/a", "denunciada", "detenido"]}}]},
            {"label": SectionLabels.DENUNCIADO_SECTION, "pattern": [{"LOWER": "pasa"}, {"LOWER": "a"}, {"LOWER": "su"}, 
                                                                    {"LOWER": {"IN":["disposicion","disposición"]}}]},
            {"label": SectionLabels.DENUNCIADO_SECTION, "pattern": [{"LOWER": "identificación"},{"LOWER": "plena"},
                                                                    {"LOWER": "de"}, {"LOWER": "los"},
                                                                    {"LOWER": "denunciados"}]},
            
            {"label": SectionLabels.DENUNCIADO_SECTION, "pattern": [{"LOWER": "datos"},{"LOWER": "personales"},
                                                                    {"LOWER": "del"}, {"LOWER": "agresor"},
                                                                    {"LOWER": "son"}]},
            
            {"label": SectionLabels.DENUNCIADO_SECTION, "pattern": [{"LOWER": "datos"},{"LOWER": "personales"},{},{},
                                                                    {"LOWER": "del"}, {"LOWER": "agresor"},
                                                                    {"LOWER": "son"}]},

            {"label": SectionLabels.DILIGENCIA_START, "pattern":[{"LOWER": "diligencia"}, {"LOWER": "de"}]},
            {"label": SectionLabels.DILIGENCIA_END, "pattern": [{"LOWER": "conste"}, {"LOWER":"y"},{"LOWER":{"IN":["certifico","certifico."]}}]},


            #--- REGLAS DE ANGEL ------------------------------------------------------------------------------
            
            # DNI OK, LO SIGUIENTE ES MEJORARLO PARA CAPTURAR "dni numero XXXXX" o "xxxxxx-letra"
            
            {"label": CustomEntityLabels.DNI, "pattern": [{"TEXT": {"REGEX": "((\d){8})"}},
                                                           {"TEXT": {"REGEX": "[A-Z]"}} ]},   
            
            {"label": CustomEntityLabels.DNI, "pattern": [{"TEXT": {"REGEX": "((\d){8})-[A-Z]"}},]},     
                                                           
            # --- PRUEBAS FALLIDAS PARA CAPTURAR DNI
             
            #{"label": CustomEntityLabels.DNI, "pattern": [{"LOWER": "dni"}, 
            #                                              {"TEXT": {"REGEX": "((\d){8})"}},
            #                                              {"TEXT": {"REGEX": "[A-Z]"}} ]},    
            
            #{"label": CustomEntityLabels.DNI, "pattern": [{"LOWER": "dni"}, 
            #                                              {"LOWER": "número"}, 
            #                                              {"TEXT": {"REGEX": "((\d){8})"}},
            #                                              {"ORTH": "-"},
            #                                              {"TEXT": {"REGEX": "[A-Z]"}} ]},    
            
            #{"label": CustomEntityLabels.DNI, "pattern": [{"LOWER": "dni"},{"LOWER": "número"},
            #                                               {"TEXT": {"REGEX": "((\d){8})-[A-Z]"}},
            #                                              ]},    
                        
            #{"label": CustomEntityLabels.DNI, "pattern": [{"TEXT": {"REGEX": "76882519[A-Z]"}}]},
            #{"label": CustomEntityLabels.DNI, "pattern": [{"TEXT": {"REGEX": "[0-9]{8}[A-Z]"}}]},
            #{"label": CustomEntityLabels.DNI, "pattern": [{"LOWER": "dni "}, {"TEXT":"76882519M"}]},
            #{"label": CustomEntityLabels.DNI, "pattern": [{"TEXT": {"REGEX": ".*?[0-9]{8}[A-Z]"}}]},
            #{"label": CustomEntityLabels.DNI, "pattern": [{"TEXT": {"REGEX": ".*?[0-9]{8}[A-Z]"}}]},
            #{"label": CustomEntityLabels.DNI, "pattern": [{"TEXT": {"REGEX": "[Dd][Nn][Ii]"}},{}, 
            #                                              {"TEXT": {"REGEX": ".*?[0-9]{8}[A-Z]"}}]},
            #{"label": CustomEntityLabels.DNI, "pattern": [{"LOWER": "dni"}, {}, {"TEXT": {"REGEX": ".*?[0-9]{8}[A-Z]"}}]},
            
            # --- PRUEBAS FALLIDAS PARA CAPTURAR DNI
                                                    
            # localizando el atestado de la primera linea
             {"label": CustomEntityLabels.ATESTADO, "pattern": [{"LOWER": "atestado"},
                                                                {"TEXT": ":"},
                                                                {"TEXT": {"REGEX": "((\d){4})/((\d){2})"}},
                                                               ]},   
            {"label": CustomEntityLabels.ATESTADO, "pattern": [{"LOWER": "atestado"},
                                                                {"TEXT": ":"},
                                                                {"TEXT": {"REGEX": "((\d){5})/((\d){2})"}},
                                                               ]},
            {"label": CustomEntityLabels.ATESTADO, "pattern": [{"LOWER": "atestado"},
                                                                {"TEXT": ":"},
                                                                {},
                                                               ]},
            # localizando elementos sueltos
            #{"label": CustomEntityLabels.OFFENCE_ELEMENT,"pattern":  [{"LOWER": "botella"}]},
              
                   
                    
          
          
            
              
           # localizando el elemento robado
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"LEMMA": "hurtar"}, {}, {"POS": "NOUN"}]},
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"LEMMA": "robar"}, {"POS": "NOUN"}]},
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"LEMMA": "robar"}, {}, {"POS": "NOUN"}]},
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"LEMMA": "sustraer"}, {"POS": "NOUN"}]},
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"LEMMA": "portar"}, {}, {"POS": "NOUN"}]},
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"LEMMA": "portar"}, {}, {}, {"POS": "NOUN"}]},
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"POS": "NOUN"}, {"LOWER": "que"},
                                                                        {"LEMMA": "haber"},{"LEMMA": "sustraer"}]},
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"POS": "NOUN"}, {"LOWER": "que"},
                                                                        {"LEMMA": "haber"},{"LEMMA": "sustraer"}]},
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"LOWER": "ticket"},{"LOWER": "valoración"},
                                                                        {"LOWER": "de"},{},{}]},
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY,"pattern":  [{"LOWER": "víctima"},{"LOWER": "llega"},
                                                                        {"LOWER": "a"},{"LOWER": "recuperar"},{"LOWER": "su"},{}]},                                              
           {"label": CustomEntityLabels.OFFENCE_ELEMENT_POSSIBLE_CONTEXT_ROBBERY,"pattern":  [{"LOWER": "haber"},{"LOWER": "sido"},
                                                                        {"LOWER": "sustraída"}]},       
            
           
           # localizando si ha habido una puerta forzada               
           {"label": CustomEntityLabels.DOOR_FORCED,"pattern":  
                                          [{"LEMMA": "forzar"}, {"LOWER": "la"},{"lOWER": "puerta"}]},
           
           {"label": CustomEntityLabels.DOOR_FORCED,"pattern":  
                                          [{"LEMMA": "romper"}, {"LOWER": "la"},{"lOWER": "puerta"}]},    
           
           {"label": CustomEntityLabels.DOOR_FORCED,"pattern":  
                                          [{"LEMMA": "fracturar"}, {"LOWER": "la"},{"lOWER": "puerta"}]},    
               
               
           {"label": CustomEntityLabels.DOOR_FORCED,"pattern":  
                                          [{"lOWER": "puerta"},{"LOWER": "se"},{"LEMMA": "encontrar"},{"LOWER": "fracturada"}]},      
               
           {"label": CustomEntityLabels.DOOR_FORCED,"pattern":  
                                          [{"lOWER": "puerta"},{"LOWER": "se"},{"LEMMA": "encontrar"},{},{"LOWER": "fracturada"}]},    
          
           # localizando si ha habido una rotura   
           {"label": CustomEntityLabels.BREAKING,"pattern":  
                                          [{"LEMMA": "reparación"}, {"LOWER": "de"}, {"LOWER": "los"},{"lOWER": "daños"}]},
               
          # localizando numero de detencioneas
          {"label": CustomEntityRelations.DETENCIONES_ANTERIORES,"pattern":  
                                          [{"TEXT":{"REGEX":"\(.*"}},{"OP":"*"},{"TEXT":{"REGEX":".*\)"}},{"lOWER": "detenciones"}, {"LOWER": "anteriores"}]},
               
               
           # localizando factores agravanes 
              {"label": CustomEntityLabels.AGRAVANTE,"pattern":  
                                          [{"LOWER": "pistola"} ]},  
                  
              {"label": CustomEntityLabels.AGRAVANTE,"pattern":  
                                          [{"LOWER": "táser"} ]}, 
              
           # localizando si ha habido intimidacion o violencia
           {"label": CustomEntityLabels.VIOLENCE,"pattern":  
                                          [{"LOWER": "detenido"} , {"LEMMA": "agredir"}]},    
               
          
           {"label": CustomEntityLabels.VIOLENCE,"pattern":  
                                          [{"LOWER": "agredirle"} ]},        
               
           # localizando si la frase incuye al perjudicado
           {"label": CustomEntityLabels.PARTE_PERJUDICADA,"pattern":  
                                          [{"LEMMA": "parte"},{"lOWER": "perjudicada"}]},
               
                 
           
           {"label": CustomEntityLabels.PARTE_PERJUDICADA,"pattern":  
                                          [{"LEMMA": "parte"},{"lOWER": "perjudicada"}]},
               
                    
          {"label": CustomEntityLabels.PARTE_PERJUDICADA, "pattern":
                                          [{"LOWER": "intervención"},{"LOWER": "policial"}, 
                                           {"LOWER": "llevada"}, {"LOWER": "a"} , {"lOWER": "cabo"}, {"lOWER": "en"},
                                           {"lOWER": "el"}, {"lOWER": "establecimiento"} , {} ] },
               
               
           {"label": CustomEntityLabels.PARTE_PERJUDICADA,"pattern":  
                                         [{"LOWER": "la"}, {"LOWER": "entidad"}, {"LOWER": "perjudicada"},{"lOWER": "es"},{}]},             
               
               
          # DETECTANDO SI UN BLOQUE PUEDE DAR PASO A OTRO DE ESE MISMO TIPO
           {"label": CustomEntityLabels.SIG_SECCION_DENUNCIADO_SECCION,"pattern":  
                                          [{"LOWER": "presentan"},{"LOWER": "en"}, 
                                           {"LOWER": "calidad"}, {"LOWER": "de"} , {"lOWER": "detenido"}]},
                      
          # DETECCION DE EL CORTE INGLES   
          {"label": CustomEntityLabels.EL_CORTE_INGLES,"pattern":  
                                          [{"LOWER": "el"},{"LOWER": "corte"}, {"lOWER": "inglés"}]},
           
          # DETECCION DE OBJETOS VALORADOS
          {"label": CustomEntityLabels.OBJETO_VALORADO,"pattern":  
                                          [{} ,{}, {"TEXT": ","} , {"LOWER": "que"},{"LOWER": "valora"}, {"lOWER": "en"}]},
          
              
           #--- REGLAS DE CARLOS------------------------------------------------------------------------------
            
            
            
           {"label": CustomEntityLabels.NUM_SOPORTE, "pattern": [{"LOWER": {"IN":["número", "numero"]}},
                                                 {"LOWER":"de"}, {"LOWER":"soporte"}, {"TEXT":{"REGEX": "[0-9A-Za-z]{9}"}}]},

           {"label": CustomEntityLabels.COMENTARIO, "pattern": [
                {"TEXT":{"REGEX":"\(.*"}},
                {"OP":"*"},
                {"TEXT":{"REGEX":".*\)"}}
            ]},

          {"label": CustomEntityLabels.TICKET, "pattern":[{"LOWER":{"IN":["ticket", "tickets", "recibo", "recibos"]}}]},
          #{"label": CustomEntityLabels.CANTIDAD, "pattern": [{"TEXT": {"REGEX": "[0-9]+([,\.\`][0-9]+)?"}}] },
              {"label": CustomEntityLabels.COSTE, "pattern": [{"TEXT": {"REGEX": "[0-9]+([,\.\`][0-9]+)?"}},
                                           {"TEXT": {"REGEX": "[Ee][Uu][Rr][Oo]"}}]},
              {"label": CustomEntityLabels.COSTE, "pattern": [{"TEXT": {"REGEX": "[0-9]+([,\.\`][0-9]+)?[Ee][Uu][Rr][Oo]"}}]}

        ]



    
def obtain_process_name (doc, span):
    end_re = re.compile("[().\-:]")
    all_caps = re.compile("[A-Z]+")
    process_name_tokens = [x.text for x in doc[span.start:span.end]]
    for j in range(span.end, len(doc)):
        if all_caps.search(doc[j].text) is not None:
            match = end_re.search(doc[j].text)
            if (match is not None):
                process_name_tokens.append(doc[j].text[:match.end()-1])
                return " ".join([x for x in process_name_tokens])
            else:
                process_name_tokens.append(doc[j].text)
        else:
            match = end_re.search(doc[j].text)
            if (match is not None):
                process_name_tokens.append(doc[j].text[:match.end()-1])
                return " ".join([x for x in process_name_tokens])

    return " ".join([x.text for x in doc[span.start:span.end]]) + " NO IDENTIFICADA"

def contains_denunciante_flag (doc):
    return any([x.label_ == SectionLabels.DENUNCIANTE_SECTION for x in doc.ents])

def contains_denunciado_flag (doc):
    return any([x.label_ == SectionLabels.DENUNCIADO_SECTION for x in doc.ents])

def contains_relacion_start (doc):
    return any([x.label_ == SectionLabels.RELACION_SECTION for x in doc.ents])

def posibles_objetos (texto):
    MiLista = ["cartera", "bolso", "mochila","coche", "motocicleta", "anillo","collar", "pulsera"]  
    return texto in MiLista
    

## PRE: ent_a and ent_b do not overlap
def entity_span_distance (ent_a, ent_b):
    return min(abs(ent_b.start-ent_a.end), abs(ent_a.start-ent_b.end))

def promote_cantidad_to_coste (doc, ent):
    WINDOW = 4
    costes = [e for e in doc.ents if e.label_ == CustomEntityLabels.COSTE]
    return any([entity_span_distance(ent, e) <= WINDOW for e in costes])

def neutral_section_starts (s):
    return NEUTRAL_START_RE.search(s) is not None

def is_section_label(ent):
    section_labels_list = [SectionLabels.RELACION_SECTION,
                           SectionLabels.DENUNCIANTE_SECTION,
                           SectionLabels.DENUNCIADO_SECTION,
                           SectionLabels.DILIGENCIA_START,
                           SectionLabels.DILIGENCIA_END]
    return ent.label_ in section_labels_list

def add_entry_dict (dict, s):
    if s not in dict:
        dict[s] = {}

def add_entry_list (dict, s):
    if s not in dict:
        dict[s] = []
#######
# It's a very flat structure: we can only find some informal subsections, along with
# a slightly more formal one-level structure of processes (diligencias)

## IMPORTANT: I'm assuming that some of the sections will only span one

# --ALGM--
def limpiar_dir(ruta):
    
    my_files = glob.glob(ruta + '/*.stxt')

    for my_file in my_files:
        try:
            os.remove(my_file)
        except OSError as e:
                print(f"Error:{ e.strerror}")


# --ALGM-- FUNCION DE POST PROCESO PARA OBTENER OTRAS ENTIDADES DENTRO DE ALGUNAS DE LAS ESTRUCTURAS HAYADAS
def post_proceso_extraccion_entidades(e1,e2):
    
    
    # ¿a continuacion viene la relacion de objetos robados?
    if e1.label_ == SectionLabels.RELACION_SECTION:
           flags.RELACION_OBJETOS = True
    
    
    # Objeto robado
    if e1.label_ == CustomEntityLabels.OFFENCE_ELEMENT_CONTEXT_ROBBERY: #and not flags.OFFENSE_ELEMENT_OK:
        doc2 = nlp(e1.text)
        if doc2[1].text == "Ticket":
           e2.palabra = doc2[4].text + " " + doc2[5].text
           e2.tipo = CustomEntityLabels.OFFENCE_ELEMENT
           e2.relacion = CustomEntityRelations.STOLEN_BY
           flags.OFFENSE_ELEMENT_OK = True
           return "OK"
        else:
            for palabra in doc2:
                if palabra.pos_ == "NOUN" and palabra.text != "víctima":
                    e2.palabra = palabra.text
                    e2.tipo = CustomEntityLabels.OFFENCE_ELEMENT
                    e2.relacion = CustomEntityRelations.STOLEN_BY
                    flags.OFFENSE_ELEMENT_OK = True
                    return "OK"
                  
                
    # Num atestado   
    elif e1.label_ == CustomEntityLabels.ATESTADO and not flags.NUMERO_ATESTADO_OK :
            num_atestado = e1.text
            lista = num_atestado.split(":")
            e2.palabra = lista[1]
            e2.palabra = e2.palabra.strip()
            e2.tipo = CustomEntityLabels.ATESTADO
            e2.relacion = CustomEntityRelations.SER
            flags.NUMERO_ATESTADO_OK = True
            return "OK"
   # Puerta forzada     
    elif e1.label_ == CustomEntityLabels.DOOR_FORCED and not flags.DOOR_FORCED_OK :
            e2.palabra = ""
            e2.tipo = CustomEntityLabels.ATESTADO
            e2.relacion= CustomEntityLabels.DOOR_FORCED
            flags.DOOR_FORCED_OK = True
            return "OK"
    # Agravante
    elif e1.label_ == CustomEntityLabels.AGRAVANTE :
            e2.palabra = e1.text
            e2.tipo = CustomEntityLabels.ATESTADO
            e2.relacion = CustomEntityLabels.AGRAVANTE
            return "OK"
    # Violencia
    elif e1.label_ == CustomEntityLabels.VIOLENCE and not flags.VIOLENCE_OK :
            e2.palabra = ""
            e2.tipo = CustomEntityLabels.ATESTADO
            e2.relacion = CustomEntityLabels.VIOLENCE
            flags.VIOLENCE_OK = True
            return "OK"
    # Rotura     
    elif e1.label_ == CustomEntityLabels.BREAKING and not flags.BREAKING_OK :
            e2.palabra = ""
            e2.tipo = CustomEntityLabels.ATESTADO
            e2.relacion = CustomEntityLabels.BREAKING
            flags.BREAKING_OK = True
            return "OK"    
        
    # Coste     
    elif e1.label_ == CustomEntityLabels.COSTE :
            num = len(e1.text)
            num = num - 6 # quitamos la palabra EUROS
            e2.palabra = e1.text[:num]
            if e2.palabra[:1] == "-" :
                num = len(e2.palabra)-1
                e2.palabra = e2.palabra[-num:]
            e2.palabra = e2.palabra.replace(",",".")    
            e2.tipo = CustomEntityLabels.COSTE
            e2.relacion = CustomEntityRelations.SER
            flags.COSTE_OK = True
            return "OK" 
        
   # detenciones anteriores 
    elif e1.label_ == CustomEntityRelations.DETENCIONES_ANTERIORES :
            index = e1.text.find(")")
            e2.palabra = e1.text[:index]
            num = len(e2.palabra)-1
            e2.palabra = e2.palabra[-num:]
            e2.tipo = CustomEntityLabels.ACCUSED
            e2.relacion = CustomEntityRelations.DETENCIONES_ANTERIORES
            flags.BREAKING_OK = True
            return "OK"  
     
        
   
    return "NULL"

# --ALGM-- FUNCIONES DE POSTPROCESO PARA OBTENER OTRAS ENTIDADES A PARTIR DE REGLAS APLICABLES A TODA LA FRASE

def procesar_owner (d,e):
    for ent in d.ents:
      if ent.label_ == CustomEntityLabels.PARTE_PERJUDICADA:  
          if ent.text[:59] == "intervención policial llevada a cabo en el Establecimiento ":
                  num = len(ent.text)-59
                  e.palabra = ent.text[-num:]            
                  e.tipo = CustomEntityLabels.OWNER
                  e.relacion = CustomEntityRelations.SER
                  flags.OWNER_OK = True
                  return "OK"
          else:
              if ent.text[:26] == "la entidad perjudicada es ":
                  num = len(ent.text)-26
                  e.palabra = ent.text[-num:]            
                  e.tipo = CustomEntityLabels.OWNER
                  e.relacion = CustomEntityRelations.SER
                  flags.OWNER_OK = True
                  return "OK"  
              else:
                 for x in d.ents:  
                   if x.label_ == "ORG" or x.label_ == CustomEntityLabels.EL_CORTE_INGLES:
                       e.palabra = x.text            
                       e.tipo = CustomEntityLabels.OWNER 
                       e.relacion = CustomEntityRelations.SER
                       flags.OWNER_OK = True
                       return "OK"               
                 
    return "NULL"

def detectar_denunciante (d,e):
    for x in d.ents:
        if x.label_ == SectionLabels.DENUNCIANTE_SECTION:
             for ent in d.ents:
              if ent.label_ == "PER":
                  e.palabra = ent.text
                  e.tipo = CustomEntityLabels.DENUNCIANTE
                  e.relacion = CustomEntityRelations.SER
                  flags.DENUNCIANTE_OK = True
                  return "OK"
    return "NULL"

def procesar_acusado (d,e,sig):
    for x in d.ents:
      if x.label_ == SectionLabels.DENUNCIADO_SECTION or sig:
         for ent in d.ents:
              if ent.label_ == "PER" or sig:
                  e.palabra = ent.text            
                  e.tipo = CustomEntityLabels.ACCUSED   
                  e.relacion = CustomEntityRelations.SER
                  flags.ACCUSED_OK = True
                  return "OK"
    return "NULL"

def detectar_si_parrafo_sig_es_denunciado_section (d):
    for x in d.ents:
      if x.label_ == CustomEntityLabels.SIG_SECCION_DENUNCIADO_SECCION:
          for ent in d.ents:
              if ent.label_ == "PER":
                  return "NULL"
              else:
                  return "OK"
    return "NULL"


def detectar_posible_objeto_robado (d,e):
    for x in d.ents:
        if x.label_ == CustomEntityLabels.OBJETO_VALORADO:
            n = 0
            posible_objeto = ""
            for palabra in d:
              n = n + 1
              if n != 1:
                  if palabra.text == ",":
                      e.palabra = posible_objeto
                      e.tipo = CustomEntityLabels.OBJETO_VALORADO
                      e2.relacion = CustomEntityRelations.SER
                      return "OK"
                  else:
                     posible_objeto = posible_objeto + " " + palabra.text
    
    for x in d.ents:
        if x.label_ == CustomEntityLabels.OFFENCE_ELEMENT_POSSIBLE_CONTEXT_ROBBERY:
            posible_objeto = ""
            for palabra in d:
              if posibles_objetos(palabra.text) :
                      posible_objeto = palabra.text
                      e.palabra = posible_objeto
                      e.tipo = CustomEntityLabels.OBJETO_VALORADO
                      e2.relacion = CustomEntityRelations.SER
                      return "OK"
                  
                     
    
    return "NULL"      


def mylista2cadena(lista):
    cadena = ""
    for element in lista:
        cadena = cadena + "(" + element.palabra + "," + element.tipo +"," + element.relacion + ")" + ";"
    return cadena

def buscar_palabras_tripletas(lista_tripletas, tipo, relacion):
    respuestas = []
    for element in lista_tripletas:
       if element.tipo == tipo and element.relacion == relacion:
           respuestas.append(element.palabra)
    return respuestas
                

#==========================================================================
# PROCESO PRINCIPAL DE FRASES
#==========================================================================


def process_file_sentences(sentences, fichero):
    extracted_info = {}
    mydoc =  []
    state = ParsingStates.MAIN_SECTION
    current_obj = 0
    current_process = 0
    current_person = 0
    current_ent = 0
    ## Flag required to look for information about a person in the next paragraph if required
    person_found = False
    dni_found = False
    dni2_found = False
    sig_seccion_acusado = False
    lista_errores = []

    object_id = ''
    process_id = ''
    person_id = ''
        
    linea = 0
    
    infofile = open("C:/Users/PC/Documents/GitHub/LegalTextExtraction/documents/"+fichero+"_info.stxt", "w") 

    for s in sentences:
        doc = nlp(s)
        
        #if doc[0].text == "Otros":
        #    print("aqui*******************")
        
        res = ""
        current_pos = 0;
        linea = linea +1
        
        # Si estamos en la seccion de objetos robados, hacemos un tratamiento especial
        if  flags.RELACION_OBJETOS == True:
            encontrado = False
            if doc[0].text == "-1":
                     encontrado = True
                     ee = entidad()
                     ee.palabra = doc[1].text
                     if ee.palabra != "ACTA":
                         ee.tipo = CustomEntityLabels.OFFENCE_ELEMENT
                         ee.relacion = CustomEntityRelations.STOLEN_BY
                         flags.OFFENSE_ELEMENT_OK = True
                         mydoc.append(ee)
                     
            else:
                    if not encontrado:
                        if doc[0].text[:1] == "-" and doc[1].text == "EUROS":
                            ee = entidad()
                            num = len(doc[0].text)-1
                            ee.palabra = doc[0].text[-num:] + " EUROS"
                            ee.tipo = CustomEntityLabels.OFFENCE_ELEMENT
                            ee.relacion = CustomEntityRelations.STOLEN_BY
                            flags.OFFENSE_ELEMENT_OK = True
                            mydoc.append(ee)
                            encontrado = True
                        else:
                            flags.RELACION_OBJETOS = False
        
        else:
         # POST-PROCESO
         for x in doc.ents:
            ee = entidad()
            #print (x.text)
            #print (x.label_)
     
            res = post_proceso_extraccion_entidades(x,ee)
            if res != "NULL":
                if res == "OK":
                    mydoc.append(ee)
                         
                else:
                    lista_errores.append(res)
        
         # OBTENCION DEL DUEÑO DEL OBJETO DE LA OFENSA    
         if not flags.OWNER_OK:
            ee = entidad()
            res = procesar_owner(doc,ee)    
            if res != "NULL":
                if res == "OK":
                        mydoc.append(ee)
                else:
                        lista_errores.append(res)
        
         if not flags.DENUNCIANTE_OK:
            ee = entidad()
            res = detectar_denunciante(doc,ee)    
            if res != "NULL":
                if res == "OK":
                        mydoc.append(ee)
                else:
                        lista_errores.append(res)
        
        
        
         # OBTENCION DEL ACUSADO
         if not flags.ACCUSED_OK:
             ee = entidad()
             res = procesar_acusado(doc,ee,sig_seccion_acusado) 
             if res != "NULL":
                if res == "OK":
                        mydoc.append(ee)
                else:
                        lista_errores.append(res)
           
                
         # COMPROBAMOS SI ESTA LINEA DA PASO A UNA SECCION DE ACUSADO
         if not flags.ACCUSED_OK:
             res = detectar_si_parrafo_sig_es_denunciado_section(doc)
             if res == "OK":
                sig_seccion_acusado = True

         # COMPROBAMOS SI ESTA LINEA INCLUYE VALORACIONES QUE PUEDAN PERMITIR ENCONTRAR UN OBJETO ROBADO        
         if not flags.OFFENSE_ELEMENT_OK:        
             ee = entidad()
             res = detectar_posible_objeto_robado(doc,ee)
             if res != "NULL":
                if res == "OK":
                        mydoc.append(ee)
                        
     
          
                        
                  
        mytexto = ""
        mytexto = mylista2cadena(mydoc)
               
        #print(f'Linea {linea}')
        #print(f'\t{[x.text for x in doc]}')
        #print(f'{[(x.text, x.label_) for x in doc.ents]}')
        

        #------------------Guardo en un fichero aparte los resultados intermedios
        
        infofile.write(f'------\n')
        infofile.write(f'Linea {linea}\n')
        infofile.write(f'------\n')
        infofile.write(f'\t{[x.text for x in doc]}\n')
        infofile.write(f'------\n')
        infofile.write(f'{[(x.text, x.label_) for x in doc.ents]}\n')
        infofile.write(f'RELACION DE OBJETOS: \t{flags.RELACION_OBJETOS}\n')
        infofile.write(f'======\n')
        #infofile.write(f'{[(x.palabra, x.tipo, x.relacion) for x in mydoc]}\n')   MAL!!! NO SACA TODOS LOS ELEMENTOS!!! (???)
        infofile.write(f'{mytexto}\n')
        infofile.write(f'======\n')
        #------------------
        #------------------
        
        
        #------------------ OLD -Primeras pruebas con codigo de Carlos
        ## handling of the transitions between parsing states
        ## NOTE that there are two dimensions: doc/paragraph and token/entity within each of them
        ##  and depending the context we have to advance differently in both of them
        if state == ParsingStates.MAIN_SECTION:
            if contains_denunciante_flag(doc):
                add_entry_dict(extracted_info, 'DENUNCIANTE')
                current_person += 1
                person_id = 'person_' + str(current_person)
                add_entry_dict(extracted_info['DENUNCIANTE'], person_id)
                add_entry_list(extracted_info['DENUNCIANTE'][person_id], 'relacionados')
                add_entry_list(extracted_info['DENUNCIANTE'][person_id], 'dni')
                add_entry_dict(extracted_info['DENUNCIANTE'][person_id], 'otros')
                state = ParsingStates.DENUNCIANTE_SECTION
            elif contains_denunciado_flag(doc):
                add_entry_dict(extracted_info, 'DENUNCIADO')
                current_person += 1
                person_id = 'person_' + str(current_person)
                add_entry_dict(extracted_info['DENUNCIADO'], person_id)
                add_entry_list(extracted_info['DENUNCIADO'][person_id], 'relacionados')
                add_entry_list(extracted_info['DENUNCIADO'][person_id], 'dni')
                add_entry_dict(extracted_info['DENUNCIADO'][person_id], 'otros')
                state = ParsingStates.DENUNCIADO_SECTION
        elif state == ParsingStates.DENUNCIANTE_SECTION or state == ParsingStates.DENUNCIADO_SECTION:
            if person_found:
                state = ParsingStates.MAIN_SECTION
                person_found = False
        elif state == ParsingStates.RELACION_OBJETOS_SECTION:
            if neutral_section_starts(s):
                state = ParsingStates.MAIN_SECTION
            else:
                # we consider one information item per paragraph
                current_obj += 1
                object_id = 'object_'+str(current_obj)

    

        ## check that if we are in the relation state and ents == 0
        if len(doc.ents) == 0 and state == ParsingStates.RELACION_OBJETOS_SECTION:
            add_entry_dict(extracted_info['OBJETOS'], object_id)
            add_entry_list(extracted_info['OBJETOS'][object_id], 'nouns')
            add_entry_list(extracted_info['OBJETOS'][object_id], 'dni')
            add_entry_list(extracted_info['OBJETOS'][object_id], 'ents')
            for nc in doc.noun_chunks:
                extracted_info['OBJETOS'][object_id]['nouns'].append(nc.text)
        else:
            current_ent = 0
            for ent in doc.ents:
                current_ent += 1
                if state == ParsingStates.MAIN_SECTION:
                    if ent.label_ == SectionLabels.RELACION_SECTION:
                        state = ParsingStates.RELACION_OBJETOS_SECTION
                        add_entry_dict(extracted_info, 'OBJETOS')
                        current_obj += 1
                        object_id = 'objeto_' + str(current_obj)
                        ## we don't add anything yet as the objects are usually lists in another paragraph
                    elif ent.label_ == SectionLabels.DILIGENCIA_START:
                        state = ParsingStates.DILIGENCIA_SECTION
                        add_entry_dict(extracted_info, 'DILIGENCIAS')
                        current_process += 1
                        process_id = 'diligencia_'+ str(current_process)
                        add_entry_dict(extracted_info['DILIGENCIAS'], process_id)
                        add_entry_dict(extracted_info['DILIGENCIAS'][process_id], 'ents')
                        extracted_info['DILIGENCIAS'][process_id]['descripcion'] = obtain_process_name(doc, ent)
                    else:
                        if ent.label_ not in extracted_info:
                            extracted_info[ent.label_] = []
                        extracted_info[ent.label_].append(ent.text)
                elif state == ParsingStates.DENUNCIANTE_SECTION:
                    if ent.label_ == 'RELACION_START':
                        state = ParsingStates.RELACION_OBJETOS_SECTION
                        add_entry_dict(extracted_info, 'OBJETOS')
                    else:
                        if ent.label_ == 'PER':
                            if not person_found:
                                extracted_info['DENUNCIANTE'][person_id]['sujeto'] = ent.text
                                person_found = True
                            else:
                                extracted_info['DENUNCIANTE'][person_id]['relacionados'].append(ent.text)
                        else:
                           if ent.label_ == 'DNI':
                                if not dni_found:
                                    extracted_info['DENUNCIANTE'][person_id]['dni'] = ent.text
                                    dni_found = True                                                         
                           else:
                               if not is_section_label(ent):
                                     add_entry_list(extracted_info['DENUNCIANTE'][person_id]['otros'], ent.label_)
                                     extracted_info['DENUNCIANTE'][person_id]['otros'][ent.label_].append(ent.text)
                elif state == ParsingStates.DENUNCIADO_SECTION:
                    if ent.label_ == 'RELACION_START':
                        state = ParsingStates.RELACION_OBJETOS_SECTION
                        add_entry_dict(extracted_info, 'OBJETOS')
                    else:
                        if ent.label_ == 'PER':
                            if not person_found:
                                extracted_info['DENUNCIADO'][person_id]['sujeto'] = ent.text
                                person_found = True
                            else:
                                extracted_info['DENUNCIADO'][person_id]['relacionados'].append(ent.text)
                        else:
                            if ent.label_ == 'DNI':
                                 if not dni2_found:
                                     extracted_info['DENUNCIADO'][person_id]['dni'] = ent.text
                                     dni2_found = True
                            else:            
                                if not is_section_label(ent):
                                      add_entry_list(extracted_info['DENUNCIADO'][person_id]['otros'], ent.label_)
                                      extracted_info['DENUNCIADO'][person_id]['otros'][ent.label_].append(ent.text)
                elif state == ParsingStates.RELACION_OBJETOS_SECTION:
                    if ent.label_ != SectionLabels.RELACION_SECTION:
                        add_entry_dict(extracted_info['OBJETOS'], object_id)
                        add_entry_list(extracted_info['OBJETOS'][object_id], 'nouns')
                        add_entry_list(extracted_info['OBJETOS'][object_id], 'ents')
                        # we have to take a look at the noun_chunks between entities, but
                        # also from the last one to the end of the document
                        if current_ent < len(doc.ents):
                            for nc  in [x for x in doc.noun_chunks if (x.start >= current_pos) and (x.end < ent.start)]:
                                extracted_info['OBJETOS'][object_id]['nouns'].append(nc.text)
                        else:
                            for nc in [x for x in doc.noun_chunks if (x.start >= ent.end)]:
                                extracted_info['OBJETOS'][object_id]['nouns'].append(nc.text)
                        ## given the way that users usually write, if we see a quantity nearby
                        ## a COSTE entity, then we promote it as COSTE as well
                        if ent.label_ == CustomEntityLabels.CANTIDAD:
                            # print(f'{ent} {ent.label_} {ent.label_}')
                            if promote_cantidad_to_coste(doc, ent):
                                ent.label_ = CustomEntityLabels.COSTE
                            extracted_info['OBJETOS'][object_id]['ents'].append(ent)
                        else:
                            if not is_section_label(ent):
                                extracted_info['OBJETOS'][object_id]['ents'].append(ent)
                elif state == ParsingStates.DILIGENCIA_SECTION:
                    if ent.label_ != SectionLabels.DILIGENCIA_END and not is_section_label(ent):
                        add_entry_list(extracted_info['DILIGENCIAS'][process_id]['ents'], ent.label_)
                        extracted_info['DILIGENCIAS'][process_id]['ents'][ent.label_].append(ent.text)
                    else:
                        state = ParsingStates.MAIN_SECTION
                current_pos = ent.end
                
    infofile.close()  
    
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    #------------------
    #------------------ Guardo en un fichero aparte la salida
    #------------------
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    outputfile = open("C:/Users/PC/Documents/GitHub/LegalTextExtraction/documents/"+fichero+"_output.stxt", "w") 
    victima = "UNKNOWN"
    empresa = ""
    acusado = "UNKNOWN"
    #--(1) encabezado
    valores = []
    valores = buscar_palabras_tripletas(mydoc, CustomEntityLabels.ATESTADO, CustomEntityRelations.SER)
    if len(valores) == 1 :
        numero_atestado = valores[0]
        numero_atestado = numero_atestado.replace("A","Atestado_")
        numero_atestado = numero_atestado.replace("/","_")
    else:
        numero_atestado = "UNKNOWN"
    outputfile.write(f'{OutputLabels.MARCA_DELITO}{numero_atestado} {OutputLabels.MARCA_TYPE},\n')
    outputfile.write(f'\t\t{OutputLabels.MARCA_DELITO}Report\n')
    outputfile.write(f'\t\t[ {OutputLabels.MARCA_CLASS} ;\n')
    outputfile.write(f'\t\t owl:complementOf [ rdf:type owl:Restriction ;\n')
    outputfile.write(f'\t\t\t  owl:onProperty {OutputLabels.MARCA_DELITO}hasOffenceCharacteristic ; \n')
    outputfile.write(f'\t\t\t  owl:someValuesFrom {OutputLabels.MARCA_DELITO}RobberyCharacteristic \n')
    outputfile.write(f'\t\t\t ] \n')
    outputfile.write(f'\t\t ] ; \n')
    #-- elementos robados
    valores = []
    valores = buscar_palabras_tripletas(mydoc, CustomEntityLabels.OFFENCE_ELEMENT, CustomEntityRelations.STOLEN_BY)
    if len(valores) > 0 :
        outputfile.write(f'\t {OutputLabels.MARCA_DELITO}IsStolen ')
        contador = 0
        for element in valores:             
                     outputfile.write(f'\t {OutputLabels.MARCA_DELITO}{element} ')
                     contador = contador + 1
                     if contador < len(valores):
                         outputfile.write(f',\n\t\t\t\t\t')
                     else:     
                         outputfile.write(f'.\n')             
    outputfile.write(f'\n\n')  
                                
    #--(2) denunciado
    valores = []
    valores = buscar_palabras_tripletas(mydoc, CustomEntityLabels.ACCUSED, CustomEntityRelations.SER)
    if len(valores) > 0 :
       acusado = valores [0]
       outputfile.write(f'{OutputLabels.MARCA_DELITO}acusado {OutputLabels.MARCA_TYPE} ,\n')
       outputfile.write(f'\t\t\t\t\t\t {OutputLabels.MARCA_DELITO}Accused .\n')
       valores = []
       valores = buscar_palabras_tripletas(mydoc, CustomEntityLabels.ACCUSED, CustomEntityRelations.DETENCIONES_ANTERIORES)
       if len(valores) > 0 :
           outputfile.write(f'\t\t\t\t{OutputLabels.MARCA_DELITO}hasOlderSentence {OutputLabels.MARCA_DELITO}Detencion .')
       outputfile.write(f'\n\n')
    
    #--(3) detenciones
    valores = []
    valores = buscar_palabras_tripletas(mydoc, CustomEntityLabels.ACCUSED, CustomEntityRelations.DETENCIONES_ANTERIORES)
    if len(valores) > 0 :
        outputfile.write(f'{OutputLabels.MARCA_DELITO}Detencion {OutputLabels.MARCA_TYPE} , \n')
        outputfile.write(f'\t\t\t\t\t\t {OutputLabels.MARCA_DELITO}PunishmentsForCrimesAgainstProperty ;\n')
        outputfile.write(f'\t\t\t\t{OutputLabels.MARCA_DELITO} num {valores[0]} .')
   
    #--(4) victima
    valores = []
    valores = buscar_palabras_tripletas(mydoc, CustomEntityLabels.DENUNCIANTE, CustomEntityRelations.SER)
    if len(valores) > 0 :
        victima = valores[0]
        outputfile.write(f'{OutputLabels.MARCA_DELITO}victima {OutputLabels.MARCA_TYPE} ,\n')
        outputfile.write(f'\t\t\t\t\t\t {OutputLabels.MARCA_DELITO}Victim ')
        
        valores = []
        valores = buscar_palabras_tripletas(mydoc, CustomEntityLabels.OWNER, CustomEntityRelations.SER)
        if len(valores) > 0 :
            outputfile.write(f';\n')
            outputfile.write(f'\t\t\t\t{OutputLabels.MARCA_DELITO}isEmployed {OutputLabels.MARCA_DELITO}{valores[0]} ')            
        
        outputfile.write(f'.\n')
        outputfile.write(f'\n\n')    
    #--(5) empresa
    valores = []
    valores = buscar_palabras_tripletas(mydoc, CustomEntityLabels.OWNER, CustomEntityRelations.SER)
    empresa = valores[0]
    if len(valores) > 0 :
        outputfile.write(f'{OutputLabels.MARCA_DELITO}empresa {OutputLabels.MARCA_TYPE} ,\n')
        outputfile.write(f'\t\t\t\t\t\t {OutputLabels.MARCA_DELITO}{empresa} .')
        outputfile.write(f'\n\n')
    
     
    #--(6) objetos robados y valoracion
    valores = []
    valores = buscar_palabras_tripletas(mydoc, CustomEntityLabels.OFFENCE_ELEMENT, CustomEntityRelations.STOLEN_BY)
    for element in valores:  
        outputfile.write(f'{OutputLabels.MARCA_DELITO}{element} {OutputLabels.MARCA_TYPE} , \n')
        outputfile.write(f'\t\t\t\t\t\t {OutputLabels.MARCA_DELITO}MovableThing ;\n')
        if empresa != "" :
            outputfile.write(f'\t\t\t\t{OutputLabels.MARCA_DELITO}BelongsTo {OutputLabels.MARCA_DELITO}{empresa} ;\n')
        outputfile.write(f'\t\t\t\t{OutputLabels.MARCA_DELITO}BelongsTo {OutputLabels.MARCA_DELITO}{victima} ;\n')
        outputfile.write(f'\t\t\t\t{OutputLabels.MARCA_DELITO}IsTheftBy {OutputLabels.MARCA_DELITO}{acusado} ;\n')
        outputfile.write(f'\t\t\t\t{OutputLabels.MARCA_DELITO}IsUsedBy {OutputLabels.MARCA_DELITO}{victima} ;\n')
        #aqui habria que mirar si hay alguna tripleta con el coste de ese elemento
        outputfile.write(f'\t\t\t\t{OutputLabels.MARCA_DELITO}ValueCost xx ')
        outputfile.write(f'.\n')
        outputfile.write(f'\n\n')                                        
   
    #--(X) fin
    outputfile.close()
    
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    
    
    return extracted_info



#==============================================================
#==============================================================
#   MAIN
#==============================================================
#==============================================================

if __name__ == '__main__':
    directorio = sys.argv[1]
    print(directorio)
    
    limpiar_dir(directorio)
    sentences = load_sentences_file_by_file(directorio)
    nlp = spacy.load(ConfigurationParams.MODEL)

    ruler = nlp.add_pipe("entity_ruler", before="ner")
    ruler.add_patterns(patterns)

    for filename in sentences:
        inicializar_flags()
        print (f'processing {filename}...')
        extracted_info = process_file_sentences(sentences[filename], filename)
        
        # ====== IMPRIMO EN PANTALLA LA INFORMACION EXTRAIDA y/o la guardo en un fichero
        #print(f'{extracted_info}')
        with open(filename+"_EXTRACTED.stxt", "w") as out:
           out.write(f'{extracted_info}') 
        # ======
        
        with open(filename+"_naive.stxt", "w") as out:
            if 'TIPO_DELITO' in extracted_info:
                out.write(f'http://tipoDelito\n')
                for x in extracted_info['TIPO_DELITO']:
                    out.write(f'\t{x}\n')
            if 'DENUNCIANTE' in extracted_info:
                for person in extracted_info['DENUNCIANTE']:
                    if 'sujeto' in extracted_info["DENUNCIANTE"][person]:
                        out.write (f'http://potencialDenunciante\n')
                        out.write (f'\thttp://potencialDenunciante/sujeto\n')
                        out.write (f'\t\t{extracted_info["DENUNCIANTE"][person]["sujeto"]}\n')
                        out.write (f'\thttp://potencialDenunciante/dni\n')
                        out.write (f'\t\t{extracted_info["DENUNCIANTE"][person]["dni"]}\n')
                        if len(extracted_info['DENUNCIANTE'][person]['relacionados']) != 0:
                            out.write (f'\thttp://denunciante/personasRelacionadas\n')
                            for ent in extracted_info['DENUNCIANTE'][person]['relacionados']:
                                out.write(f'\t\t{ent}\n')
                        if len(extracted_info['DENUNCIANTE'][person]['otros']) != 0:
                            for label in extracted_info['DENUNCIANTE'][person]['otros']:
                                out.write(f'\thttp://denunciante/otrasEntsRelacionadas/{label}\n')
                                for ent in extracted_info['DENUNCIANTE'][person]['otros'][label]:
                                    out.write(f'\t\t{ent}\n')
            if 'DENUNCIADO' in extracted_info:
                for person in extracted_info['DENUNCIADO']:
                    if 'sujeto' in extracted_info['DENUNCIADO'][person]:
                        out.write (f'http://denunciado\n')
                        out.write (f'\thttp://denunciado/sujeto\n')
                        out.write (f'\t\t{extracted_info["DENUNCIADO"][person]["sujeto"]}\n')
                        out.write (f'\thttp://denunciado/dni\n')
                        out.write (f'\t\t{extracted_info["DENUNCIADO"][person]["dni"]}\n')
                        if len(extracted_info['DENUNCIADO'][person]['relacionados']) != 0:
                            out.write (f'\thttp://denunciado/personasRelacionadas\n')
                            for ent in extracted_info['DENUNCIADO'][person]['relacionados']:
                                out.write(f'\t\t{ent}\n')
                        if len(extracted_info['DENUNCIADO'][person]['otros']) != 0:
                            for label in extracted_info['DENUNCIADO'][person]['otros']:
                                out.write(f'\thttp://denunciado/otrasEntsRelacionadas/{label}\n')
                                for ent in extracted_info['DENUNCIADO'][person]['otros'][label]:
                                    out.write(f'\t\t{ent}\n')
            if 'OBJETOS' in extracted_info:
                out.write(f'http://objetos\n')
                for object_name in extracted_info['OBJETOS']:
                    out.write(f'\thttp://objetos/{object_name}\n')
                    for nc in extracted_info['OBJETOS'][object_name]['nouns']:
                        out.write(f'\t\tNC: {nc}\n')
                    for ent in extracted_info['OBJETOS'][object_name]['ents']:
                        out.write(f'\t\tENT: {ent.label_} URI: http://objetos/{object_name}/{ent.text}\n')
            if 'DILIGENCIAS' in extracted_info:
                out.write(f'http//diligencias\n')
                for process_id in extracted_info['DILIGENCIAS']:
                    out.write(f'\thttp://diligencias/{process_id}\n')
                    out.write(f'\t\thttp://descripcion {extracted_info["DILIGENCIAS"][process_id]["descripcion"]}\n')
                    for ent_type in extracted_info['DILIGENCIAS'][process_id]['ents']:
                        out.write(f'\t\t\thttp://{ent_type}\n')
                        for ent in extracted_info['DILIGENCIAS'][process_id]['ents'][ent_type]:
                            out.write(f'\t\t\t\t{ent}\n')
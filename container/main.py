import spacy
from spacy.matcher import DependencyMatcher
from typing import List

def extract_sentences(doc) -> List[str]:  
    sentences = [sent.text for sent in doc.sents]
    return sentences

def dependency_matcher(nlp, ent_cause, ent_effect): 
    '''
    Input:
    - nlp (English): A spacy model with customized ner that can recognize entities of interest
    - ent_cause: a string corresponding to the first entity type of interest (cause) as used in nlp model (ex: "COMPOUND"). 
    - ent_effect: a string corresponding to the second entity type of interest (effect) as used in nlp model (ex: "PHENOTYPE"). 
    Output:
    - matcher: DependencyMatcher with the pattern 'LINKING_VERB' added
    '''
    matcher = DependencyMatcher(nlp.vocab)
    
    # Create pattern that explains the relation: a verb is an (indirect) ancestor of a phenotype and a compound
    '''
    Every dictionary contains one node in the dependency tree
    RIGHT_ID describes the node (e.g. the verb, the cause or the effect)
    RIGHT_ATTRS describes how the model can recognize this node
    LEFT_ID describes where the node is linked to (the cause and the effect are linked to the verb
    REL_OP describes the relation between the two nodes ('>>' is indirect child)
    '''
    pattern = [
        {'RIGHT_ID': 'linking_verb',
         'RIGHT_ATTRS': {'POS':'VERB'}
        },
        {'LEFT_ID':'linking_verb',
         "REL_OP": ">>",
         "RIGHT_ID": "cause",
         "RIGHT_ATTRS": {"ENT_TYPE": ent_cause}
        },
        {"LEFT_ID": "linking_verb",
         "REL_OP": ">>",
         "RIGHT_ID": "effect",
         "RIGHT_ATTRS": {"ENT_TYPE": ent_effect}
        }
    ] 
    # Add the pattern to the matcher and call it "LINKING_VERB"
    matcher.add("LINKING_VERB", [pattern])
    return matcher

def extract_relationships(sentence_doc,matcher, causal_verbs):
    matches = matcher(sentence_doc)
    # extract (cause, verb, effect) triplets from a sentence, filtering for causal verbs
    rels = [(sentence_doc[match[1][1]].text,sentence_doc[match[1][0]].text,sentence_doc[match[1][2]].text)for match in matches if sentence_doc[match[1][0]].lemma_ in causal_verbs] 
    return rels

nlp = spacy.load("en_tox")
nlp.add_pipe("merge_entities")

#matcher = dependency_matcher(nlp, "COMPOUND", "PHENOTYPE")

causal_verbs = ['increase', 'produce', 'cause', 'induce', 'generate', 'effect', 'provoke', 'arouse', 'elicit', 'lead', 'trigger','derive', 'associate', 'relate', 'link', 'stem', 'originate', 'lead', 'bring', 'result', 'inhibit', 'elevate', 'diminish', "exacerbate", "decrease"]

def entox_parse(text, nlp=nlp,cause="COMPOUND", effect="PHENOTYPE", causal_verbs=causal_verbs): 
    # cause and effect are strings and need to be an entity type recognized by the en_tox model
    # they can both be "PHENOTYPE"
    matcher = dependency_matcher(nlp, cause, effect)
    doc = nlp(text)
    sentences = extract_sentences(doc)
    docs = [nlp(sentence) for sentence in sentences]
    relations = [extract_relationships(sentence_doc,matcher, causal_verbs) for sentence_doc in docs]
    # remove empty lists and flatten
    relations = [item for sublist in relations for item in sublist]
    if relations == []:
        relations = "No relationship found"
    return relations

'''
Marie P.F. Corradi, Iris den Hertog, Marc A.T. Teunis -  CC-BY, NC - Data Science INT Hogeschool Utrecht
'''
import spacy
from metapub import PubMedFetcher
from Bio.Entrez import efetch
import pandas as pd
import re
from spacy.matcher import DependencyMatcher
from scispacy.abbreviation import AbbreviationDetector
from urllib.error import HTTPError 
from http.client import IncompleteRead

def fetch_abstract(pmid):
    # Get abstract text
    handle = Entrez.efetch(db='pubmed', id=pmid, retmode='text', rettype='abstract')
    try:
        abstract = handle.read() 
    except IncompleteRead:
        abstract = "incomplete"
        print("incomplete")
    handle.close()
    return abstract

def get_df_pmid_sents(nlp, pmids, abstracts):
    '''
    Input:
    - nlp (English): a spacy English model
    - abstracts (dict): a dictionnary where each pmid (PubMed identifier) is a key and the corresponding value is a string containing the text of the abstract from corresponsing article
    Output:
    - df (pd.DataFrame): A dataframe containing columns 'Pmid' and 'Sentences', where each row represents a sentence and its corresponding pmid, which are both strings.
    '''
    # Create a list of dictionaries, including a pmid and a list of sentences
    pmid_sents = []

    # Create a list of sentences for every pmid
    for pmid in abstracts.keys():
        sents = []
        doc = nlp(abstracts[pmid])
        # Iterate over every sentence and replace newlines with spaces to avoid misanalysis of the sentence
        for sent in doc.sents:
            sent = str(sent).replace('\n', ' ')
            sents.append(sent)
        
        # Create a dictionary in the form {'Pmid':pmid, 'Sentences':[sents]} and append each dictionary to pmid_sents
        dict = {'Pmid':pmid, 'Sentences':sents}
        pmid_sents.append(dict)
     
    df = pd.DataFrame(pmid_sents)
    
    # Explode the dataframe in order to create a separate row for every sentence
    df = df.explode('Sentences', ignore_index = True)
    
    return df


def find_both_ent_types(nlp, ent_cause, ent_effect, list_of_strings):
    '''
    Input:
    - nlp (English): An English spacy model with customized ner that can recognize phenotypes and compounds
    - ent_cause: a string corresponding to the first entity type of interest (cause) as used in nlp model (ex: "COMPOUND")
    - ent_effect: a string corresponding to the second entity type of interest (effect) as used in nlp model (ex: "PHENOTYPE") 
      Can be the same as ent_cause, if you are interested in relationships between similar entities
    - list_of_strings (List): A list of the values (strings) of a column of a dataframe
    Ouput:
    A series containing the following values per row:
    - cause_effect (Boolean): True if the sentence contains both a entity types 1 and 2 (cause and effect), else False
    - ent1 (String): All entity1 (cause) mentions in the sentence
    - ent2 String): All entity2 (effect) mentions in the sentence
    '''
    doc = nlp(str(list_of_strings))

    cause_effect = False
    
    # Create a list of both entities
    # Iterate over entities of the sentence and check whether the label is either that of entity1 or entity2, add the text to the list
    ent1=[ent.text for ent in doc.ents if ent.label_==ent_cause]
    ent2=[ent.text for ent in doc.ents if ent.label_==ent_effect]

    # If the list of both entities contain a value and the two entities are of different type, cause_effect is True
    if ent_cause!=ent_effect and ent1 and ent2:
        cause_effect = True
    # If the two entities are the same type and there is at least two entities in the sentence, cause_effect is True as well
    elif ent_cause==ent_effect and len(ent1)>=2:
        cause_effect = True
            
    # Return the value of comp_pheno (True or False) and the lists of compounds and phenotypes for every sentence in the dataframe
    return pd.Series([cause_effect,ent1,ent2])

def get_df_relations(nlp,ent_cause,ent_effect, df):
    '''
    Input: 
    - nlp (English): An English spacy model with customized ner that can recognize entity1 and entity2 types
    - ent_cause: a string corresponding to the first entity type of interest (cause) as used in nlp model (ex: "COMPOUND")
    - ent_effect: a string corresponding to the second entity type of interest (effect) as used in nlp model (ex: "PHENOTYPE")
    - df (pd.DataFrame): A dataframe of strings with at least the following column(s): 'Sentences'
    Output:
    - df (pd.DataFrame): A dataframe of strings with at least the column(s): 'Sentences', ent_cause, ent_effect
    '''
        
    # Filter out all sentences that contain both a compound and a phenotype
    # Apply the function 'find_comp_pheno' to the dataframe and create a new column for every returned value
    df[['Has cause_effect', ent_cause, ent_effect]] = df.apply(lambda x: find_both_ent_types(nlp, ent_cause, ent_effect, x["Sentences"]), axis=1)

    # Drop all rows where comp_pheno is False
    df.drop(df[df['Has cause_effect'] == False].index, inplace=True)

    df.reset_index(drop=True, inplace=True)
    df.drop('Has cause_effect', axis=1, inplace=True)
    
    return df

def dependency_matcher(nlp, ent_cause, ent_effect): 
    '''
    Input:
    - nlp (English): An English spacy model with customized ner that can recognize phenotypes and compounds
    - ent_cause: a string corresponding to the first entity type of interest (cause) as used in nlp model (ex: "COMPOUND"). 
    - ent_effect: a string corresponding to the second entity type of interest (effect) as used in nlp model (ex: "PHENOTYPE"). 
    Output:
    - Matcher: DependencyMatcher with the pattern 'LINKING_VERB' added
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


def get_df_dependencyMatcher(nlp, df, matcher, causal_verbs):
    '''
    Input:
    - nlp (English): An English Spacy model with customized ner that can recognize phenotypes and compounds, and 'abbreviation_detector' in the pipeline
    - df (pd.DataFrame): A dataframe of strings with at least the following column(s): 'Sentences'
    - matcher (DependencyMatcher): the matcher retrieved from the previous function that contains the 'LINKING_VERB' pattern
    - causal_verbs (List): A list of strings containing the lemma of causal verbs
    Output:
    - df (pd.DataFrame): A dataframe of strings with at least the column(s): 'Sentences', 'Has Match', 'Causes Match', 'Effects Match', 'Verb Match'
    '''
    
    causal_list = []
    causes_list = []
    effects_list = []
    linking_verbs = []
    
    for sent in df['Sentences']:
        doc = nlp(sent)
        causal = False
        causes = []
        effects = []
        verbs = []
    
        # Remove abbreviation from sentence to avoid double patterns (e.g. 'Valproic acid (VPA)' becomes 'Valproic acid ()')
        for word in doc._.abbreviations:
            if str(word) in sent:
                sent = sent.replace(str(word), "")

        # Create new doc object (without abbreviations)
        doc = nlp(sent)

        # Retokenize: make every entity one token (e.g. 'valproic acid')
        with doc.retokenize() as retokenizer:
            for ent in doc.ents:
                retokenizer.merge(doc[ent.start:ent.end])

        # Apply matcher on the doc object
        matches = matcher(doc)

        '''
        A match consists of a match_id and token_ids
        match_id is a unique number for every match, token_ids is a set of numbers for every token that is part of the match
        token_ids[0] is the verb
        token_ids[1] is the (entity) cause
        token_ids[2] is the (entity) effect
        '''
        for match in matches:
            match_id, token_ids = match

            # If the lemma of the verb is a causal verb, append the text of the verb, compound and phenotype to the corresponding lists
            # change 'causal' to True
            if doc[token_ids[0]].lemma_ in causal_verbs:
                verbs.append(doc[token_ids[0]].text)
                causes.append(doc[token_ids[1]].text)
                effects.append(doc[token_ids[2]].text)
                causal = True
        
        # Append the lists (causes, effects, verbs, causal) of every sentences to the corresponding lists. This creates lists of lists.
        causal_list.append(causal)
        causes_list.append(causes)
        effects_list.append(effects)
        linking_verbs.append(verbs)
        
    df['Has Match'] = causal_list
    df['Cause Match'] = causes_list
    df['Effect Match'] = effects_list
    df['Verb Match'] = linking_verbs
    
    return df
       
def get_lemma(a_verb,nlp):
    doc=nlp(a_verb)
    return doc[0].lemma_

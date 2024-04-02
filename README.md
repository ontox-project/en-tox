# en-tox: a simple NLP model to extract toxicological information from scientific text. [![DOI](https://zenodo.org/badge/731658957.svg)](https://zenodo.org/doi/10.5281/zenodo.10610596)


This is the repository containing the work described in the paper "The application of Natural Language Processing for the extraction of toxicological mechanistic information with the container to run the en-tox model extracting relationships between toxicological entities". The "article" folder contains the code  and data files used for the study. The "container" folder contains all code to run the NLP pipeline in isolation. This comprises an updated version of the NER model (to spaCy v3.6) as well as a cleaned-up relationship extraction pipeline, packaged in a Flask application and a Docker container. Instructions on how to run the later are detailed below.

## The en-tox model

The Named Entity Recognition model used in the study, referred to here as en-tox, was developed in the scope of the [DARTPaths project](https://nc3rs.org.uk/crackit/dartpaths). It was trained to recognize 7 entity types, which were annotated using the following instructions:
* COMPOUND: the smallest unit of a generic/molecular name. For example, we would label “butafenacil” or “C20H18ClF3N2O6” as a compound, but not categories of compounds, such as “herbicide”.
* PHENOTYPE: We include the "largest possible" phenotype, i.e., the most specific possible. For example in “increased death of liver cells”, we have phenotype (“death”), attribute/modifier (“increased”) and object (“liver cells”). We then label the complete group of words. However, do not include negations in the phenotype. For example, if the text is “no increase of liver weight is observed”, the phenotype should be “increase of liver weight”.
* ORGANISM: We consider both the biological meaning and the “implied” meaning. For example, we will label “plant” as an organism, even if it is not species-specific. Similarly, we will label “sample” or “participant” as organisms, as they refer to a human organism
* EXPOSURE_ROUTE: The way the compound is administered (ex: “inhaled”, “ingested”, etc.).
* DOSE: We consider dose as number+unit (ex: “20mg/L”), or as a dose estimate (for example, “IC50”, “NOEC”, etc.)
* IN_VITRO_VIVO: Words that indicate the conditions under which the study was conducted, for example “cells”/”cell lines” or “organoids”
* PARENT_VS_OFFSPRING: In which of the two the effects are observed, for example “embryo”, “F1”, etc.

Around 8.000 sentences were annotated, corresponding to about 5.000 sentences from 100 Pubmed articles and 3.000 sentences from 200 ECHA reports.
We report a global F1 score  on the training corpus of 0.72, and the following F1-scores per entity type:

| Entity              | F1 score |
| ------------------- | -------- |
| COMPOUND            | 0.88     |
| PHENOTYPE           | 0.56     |
| ORGANISM            | 0.79     |
| EXPOSURE_ROUTE      | 0.59     |
| DOSE                | 0.80     |
| IN_VITRO_VIVO       | 0.55     |
| PARENT_VS_OFFSPRING | 0.83     |

The Relationship Extraction module is based on semantic rules and based on the DependencyMatcher from spaCy. Details can be found in the paper or in article/code/utils.py, function dependency_matcher.

## Build & Run the Relationship Extraction pipeline with Docker

Run in your terminal, from the "container" directory:

```
docker build -t entox .
docker run -p 5000:5000 entox
python app.py
```

In a separate terminal, run:

```
curl -X POST -H "Content-Type: application/json" -d '{"text": "$YOUR_TEXT", "cause": "$YOUR_CAUSE", "effect": "YOUR_EFFECT"}' http://localhost:5068/relationships
```

where "text" is the text you are interested in extracting relationship from, "cause" is the cause you are interested in ("COMPOUND" or "PHENOTYPE") and effect the outcome the cause triggers ("PHENOTYPE").
The output obtained will be a list of triplets representing all relationships extracted (if any) as (cause, causal verb, effect).

For ease of use, the pre-built image is available on [DockerHub](https://hub.docker.com/repository/docker/marieco/entox/general).

You can also directly integrate/adapt the model and code (main.py) in your own pipeline. In this case please reference our work as [xxx ref Corradi et al.]

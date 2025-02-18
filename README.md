# MiCRA: a minimal pipeline for functional microbiome information retrieval using Natural Language Processing and Biomedical Ontologies

## Repository for Thesis Project

**Student:** Madalena Girão

**Supervisor:** Francisco Couto

**Co-supervisor:** Ana Margarida Fortes

### Abstract:
Abiotic stresses, such as drought and salinity, pose significant challenges to modern agriculture, threatening global food security amid increasing climate variability. Microbial communities, particularly those associated with plants and crops, offer a promising approach for mitigating the impacts of these stresses. This dissertation introduces MiCRA (Microbial Communities for Regenerative Agriculture), an innovative natural language processing pipeline designed to extract, process, and organize knowledge about microbe-mediated stress tolerance in plants. The system combines text mining techniques and the NCBI Organismal Taxonomy Ontology to generate robust datasets, capturing relationships between microorganisms, plants, and stresses from biomedical literature. The primary goal is to empower researchers to explore sustainable, microbe-based regenerative agriculture solutions for enhancing plant resilience to various types of abiotic stress.

This work resulted in the creation of a comprehensive gold-standard *corpus*, based on the manual curation of an automatically generated silver-standard *corpus*. The initial *corpus* was partially evaluated by nine curators from the fields of Biology and Biochemistry, achieving an accuracy of 55.37% and an F-score of 71.27%, with an inter-curator agreement level of 88.97%. The Microbe-Mediated Plant Abiotic Stress Tolerance (2M-PAST) *corpus* comprises 2718 relationships derived from 8154 annotations, including 440 microbial entities, 20 stress entities, and 16 plant entities. Key findings include the validation of co-occurrence-based methods for Relation Extraction (RE) and the identification of significant gaps in existing ontological resources. Furthermore, subsequent data analysis revealed textual patterns that can be leveraged to further refine the pipeline and improve methodological strategies.

Despite opportunities for improvement, MiCRA's simplified design, which integrates lexicon-based entity recognition and sentence-level RE, highlights its potential to drive advancements in regenerative agriculture. Moreover, the results aim to promote the development and adoption of task-specific systems in biomedical text processing, establishing them as a viable and more sustainable alternative to large language models, such as ChatGPT. The public availability of this tool, along with the associated *corpus*, cements its value as a strategic resource for agricultural research and development on a large scale.

### Relations:
Microdrygrape Project @ FCUL

Bayer Digital Campus Challenge 2023 (Data-Driven Farming)


### Important References:
Sousa, D., Lamurias, A., and Couto, F. M. (2019). A silver standard corpus of human phenotype-gene relations. NAACL HLT 2019 - 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies - Proceedings of the Conference, 1:1487–1492 (https://aclanthology.org/N19-1152/)

---

## Dependencies

* Python = 3.9
  
* Pre-processing:
    * [Natural Language Toolkit](https://www.nltk.org/)
    * [Owlready2](https://owlready2.readthedocs.io/en/v0.47/)
    
* Term Recognition:
    * [MER (Minimal Named-Entity Recognizer)](https://github.com/lasigeBioTM/MER)
    * [NCBI Organismal Classification Ontology](https://bioportal.bioontology.org/ontologies/NCBITAXON)
      
* Data Visualization:
    * [Jupyter](https://jupyter.org/)
    * [Pandas](https://pandas.pydata.org/docs/getting_started/overview.html)
    * [NetworkX](https://networkx.org/)

## Getting Started

```bash
 cd bin/
 git clone git@github.com:lasigeBioTM/MER.git
 wget https://purl.obolibrary.org/obo/ncbitaxon.owl
```

### Creating lexicons

```bash
mkdir logfiles || True
python3 ./bin/produce_data_files_classes.py | tee logfiles/01_lexicon_creation.txt
```

Generates lexicon files for microorganism and plant entities (stress entity lexicon was manually created and already exists in ./bin/MER/data/)

### Crosschecking entities (OPTIONAL)

```bash
python3 tools/crosscheck.py | tee logfiles/02_crosscheck.txt
```
Checks if all entities in the Ground Truth Dataset (GTD) were retrieved from the ontology by the lexicon creation script (for entity recognition optimization).

## Usage

### Get PubMed Central (PMC) IDs

```bash
python3 src/get_pmcids.py | tee logfiles/03_get_pmcids.txt
```
Creates a text file for each stress type containing the retrieved PMCIDs.


### Extract articles
```bash
python3 src/write_files.py | tee logfiles/04_write_files.txt
```
Takes every PMCID and extracts the corresponding article, retrieving textual information and ignoring tables, figures and supplemental data.

### Get raw dataset

```bash
python3 src/get_raw_dataset.py | tee logfiles/05_get_raw_dataset.txt
```
Processes every article to obtain dataset entries pertaining to microorganism-stress-plant relations based on entity co-occurrence at sentence-level.


### Review relations in dataset (Use of script is OPTIONAL)

```bash
python3 src/check_relations.py
```
A terminal-based tool for validating dataset entries which relies on user input, and ultimately creates a final, curated *corpus*.


### Get dataset features and combinations info (OPTIONAL)

```bash
python3 src/dataset_profile.py
```
Creates a text file with dataset features (positive-negative instance ratio, most common entities for each type, etc), and separate files for the most combinations of entities.
* Creates: 
    * **info/dataset_profile.txt** 
    * **info/combinations_ALL.txt**
    * **info/combinations_cold.txt** 
    * **info/combinations_drought.txt**
    * **info/combinations_heat.txt**
    * **info/combinations_salt.txt**


### Create model files (OPTIONAL)

```bash
python3 src/get_model_files.py
```
Creates annotated .tsv files for model development (training and testing) after handling entitiy synonymy.

## Configuration

* ### bin/
    * **MER/**
        * **data/**
            * __stress_links.tsv__
            * __stress_synonyms.txt__
            * __stress_word1.txt__
            * __stress_word2.txt__
            * __stress_words.txt__
            * __stress_words2.txt__
    * **nltk_data/**
    * *classes_microorganisms.txt*
    * *classes_plant.txt*
    * **produce_data_files_classes.py**
    
* ### 2M-PAST/
    * **14_09_2024_corpus/**
        * **info/**
            * **combinations_ALL.txt**
            * **combinations_cold.txt**
            * **combinations_drought.txt**
            * **combinations_heat.txt**
            * **combinations_salt.txt**
            * **dataset_profile.txt**
        * **instance_types**
            * **dataset_negatives.txt**
            * **dataset_positives.txt**
            * **NO_combination.txt**
            * **NO_mixedEntities.txt**
            * **NO_mutants.txt**
            * **NO_norelation.txt**
            * **NO_products.txt**
            * **NO_relation2.txt**
            * **YES_context.txt**
            * **YES_direct.txt**
            * **YES_indirect.txt**
        * **model_data**
            * **2mpast_test.tsv**
            * **2mpast_train.tsv**
        * __Checked_DS.txt__
  
          

* ### GTD/
    * __article_list.csv__
    * __GTD.txt__
    
* ### src/
    * **check_relations.py**
    * **dataset_profile.py**
    * **get_model_files.py**
    * **get_pmcids.py**
    * **get_raw_dataset.py**
    * **write_files.py**

* ### tools/
    * **crosscheck.py**
    * **knowledge_graph.ipynb**
    * **word_frequency.ipynb**
  
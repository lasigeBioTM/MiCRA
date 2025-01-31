## Repository for Thesis Project entitled "MiCRA: a minimal pipeline for functional microbiome information retrieval using Natural Language Processing and Biomedical Ontologies"

Student: Madalena Girão

Supervisor: Francisco Couto

Co-supervisor: Ana Margarida Fortes

```bash
# Creates dataset information files inside info/
*python3* src/datasetProfile.py
```

### Abstract:
Abiotic stresses, such as drought and salinity, pose significant challenges to modern agriculture, threatening global food security amid increasing climate variability. Microbial communities, particularly those associated with plants and crops, offer a promising approach for mitigating the impacts of these stresses. This dissertation introduces MiCRA (Microbial Communities for Regenerative Agriculture), an innovative natural language processing pipeline designed to extract, process, and organize knowledge about microbe-mediated stress tolerance in plants. The system combines text mining techniques and the NCBI Organismal Taxonomy Ontology to generate robust datasets, capturing relationships between microorganisms, plants, and stresses from biomedical literature. The primary goal is to empower researchers to explore sustainable, microbe-based regenerative agriculture solutions for enhancing plant resilience to various types of abiotic stress.

This work resulted in the creation of a comprehensive gold-standard *corpus*, based on the manual curation of an automatically generated silver-standard *corpus*. The initial *corpus* was partially evaluated by nine curators from the fields of Biology and Biochemistry, achieving an accuracy of 55.37% and an F-score of 71.27%, with an inter-curator agreement level of 88.97%. The Microbe-Mediated Plant Abiotic Stress Tolerance (2M-PAST) *corpus* comprises 2718 relationships derived from 8154 annotations, including 440 microbial entities, 20 stress entities, and 16 plant entities. Key findings include the validation of co-occurrence-based methods for Relation Extraction (RE) and the identification of significant gaps in existing ontological resources. Furthermore, subsequent data analysis revealed textual patterns that can be leveraged to further refine the pipeline and improve methodological strategies.

Despite opportunities for improvement, MiCRA's simplified design, which integrates lexicon-based entity recognition and sentence-level RE, highlights its potential to drive advancements in regenerative agriculture. Moreover, the results aim to promote the development and adoption of task-specific systems in biomedical text processing, establishing them as a viable and more sustainable alternative to large language models, such as ChatGPT. The public availability of this tool, along with the associated *corpus*, cements its value as a strategic resource for agricultural research and development on a large scale.

### Relations:
Microdrygrape Project @ FCUL

Bayer Digital Campus Challenge 2023 (Data-Driven Farming)


### Important References:
Sousa, D., Lamurias, A., and Couto, F. M. (2019). A silver standard corpus of human phenotype-gene relations. NAACL HLT 2019 - 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies - Proceedings of the Conference, 1:1487–1492 (https://aclanthology.org/N19-1152/)


## PIPELINE

**HOME DIRECTORY: ~/MiCRA**

**Required packages: pandas, owlready2, nltk**

1. Add ‘classes_microorganisms.txt’ and ‘classes_plants.txt’ to directory ./bin/MER

**Required format for each file: [CLASS NAME] | [CLASS IRI]**

```
Chlorarachniophyceae | http://purl.obolibrary.org/obo/NCBITaxon_29197
Cryptophyceae | http://purl.obolibrary.org/obo/NCBITaxon_3027
Dinophyceae | http://purl.obolibrary.org/obo/NCBITaxon_2864
Glaucocystophyceae | http://purl.obolibrary.org/obo/NCBITaxon_38254
Haptophyta | http://purl.obolibrary.org/obo/NCBITaxon_2608109
Ochrophyta | http://purl.obolibrary.org/obo/NCBITaxon_2696291
Rhodophyta | http://purl.obolibrary.org/obo/NCBITaxon_2763
Viridiplantae | http://purl.obolibrary.org/obo/NCBITaxon_33090
```

---

2. Create directory for MER files and produce them

```bash
python3 ./bin/produce_data_files_classes.py | tee logfiles/01_lexicon_creation.txt
```

---

3. Crosscheck dataset plant and microorganism entities between ground truth dataset and extracted classes in MER files (OPTIONAL)

```bash
python3 tools/crosscheck.py | tee logfiles/02_crosscheck.txt
```

---

4. Get PMCIDs for each stress term in MER stress lexicon

```bash
python3 src/get_pmcids.py | tee logfiles/03_get_pmcids.txt
```

---

5. Create raw corpus from every article in PMCID list files

```bash
python3 src/write_files.py | tee logfiles/04_write_files.txt
```

---

6. Create unannotated dataset

```bash
python3 src/get_raw_dataset.py | tee logfiles/05_get_raw_dataset.txt
```

---

7. Review relations in dataset - manually or with script

```bash
python3 src/check_relations.py
```

---

8. Get dataset features and combinations info (OPTIONAL)

```bash
# Creates dataset information files inside info/ and final dataset with handled synonyms inside dataset/
python3 src/datasetProfile.py
```

---

9. Get .csv files with annotated entities for model development (OPTIONAL)

```bash
python3 src/get_model_files.py
```

---
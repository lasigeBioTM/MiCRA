import os
import subprocess
import time
import re
import nltk.data


stress_list = ['drought', 'salt', 'cold', 'heat']
file_types = ['abstracts', 'fulltexts']
data_sources = ['microorganisms', 'stress', 'plants']


################################################
#        HANDLING ABBREVIATIONS IN TEXT        #
################################################


def generate_abbreviations(taxa_file):
    """Called by the get_dataset_full() function. Generate a dictionary of abbreviations for each taxon name.
    
    :param taxa_file (list): full taxonomic names (str)
    :return dict: dictionary of type {'abbreviation_O1': 'full_name_O1', 'abbreviation_O2': 'full_name_O2', ...}
    """

    abbreviation_dict = {}

    with open(taxa_file, 'r', encoding = 'utf-8') as file:
        taxon_names = [line.strip() for line in file.readlines()]


        patterns = [
        re.compile(r'\bfung\w*'),               # Matches words starting with "fung" (e.g., fungus, fungi)
        re.compile(r'\byeast\w*'),              # Matches words starting with "yeast" (e.g., yeast, yeasts)
        re.compile(r'\bslime\w*'),              # Matches words starting with "slime" (e.g., slime, slimes)
        re.compile(r'\balgae\w*'),              # Matches words starting with "algae"
        re.compile(r'\bplants\w*'),             # Matches words starting with "plants"
        re.compile(r'\bmildew\w*'),             # Matches words starting with "mildew"
        re.compile(r'\bgroup\w*'),              # Matches words starting with "group"
        re.compile(r'\bclade\w*'),              # Matches words starting with "clade"
        re.compile(r'\bsubtype\w*'),            # Matches words starting with "subtype"
        re.compile(r'\w*virus\b'),              # Matches words ending with "virus" (e.g., coronavirus, retrovirus)
        re.compile(r'\bx\b'),                   # Matches lines with hybrid species
        re.compile(r'\S_\S'),                   # Matches lines with underscores
        ]


        # Check if any part matches any of the patterns
        for full_name in taxon_names:
            parts = full_name.split()

            if (
                len(parts) > 1
                and len(parts) < 3
                and parts[0].isalpha()
                and parts[1].lower() not in ['sp.', 'cf.']
                and parts[1].isalpha()
                and not any(re.search(pattern, part.lower()) for pattern in patterns for part in parts)
                and ' '.join(parts[1:]).lower() != 'incertae sedis'
                ):
                abbreviation = f"{parts[0][0]}. {' '.join(parts[1:])}"
                abbreviation_dict[abbreviation] = full_name
    
    
    return abbreviation_dict



def replace_abbreviations_in_text(text, patterns, sorted_abbreviations, abbreviations_dict):
    """Called by the create_dataset() function. Replace abbreviations in the text with their corresponding full taxon names.
    
    :param text (str): input text with possible abbreviations
    :param patterns (list): list of text patterns to match and edit text accordingly
    :param sorted_abbreviations (list): list of abbreviations sorted by length
    :param abbreviations_dict (dict): dictionary mapping abbreviations (keys) to full taxon names (values)
    :return str: sentence with abbreviations replaced by full taxon names
    :return side effect: overwrites original text file to replace abbreviations with full names
    """

    for i, pattern in enumerate(patterns):
        if pattern.search(text):
            text = pattern.sub(abbreviations_dict[sorted_abbreviations[i]], text)

    return text




##############################
#     GETTING ANNOTATIONS    #
##############################


def get_annotations(sentence, filename):
    """Called by the create_dataset() function. Gets annotations for input text and handles partial annotations to keep longer ones (more specific) by checking for
    annotations matching starting and ending positions
    --> Ex: [285,297,'Enterococcus'] and [285,307,'Enterococcus facecalis']

    :param sentence (str): input text
    :param filename (str): article identifier from which input text originates
    :return list: final annotations (most specific ones)
    """

    original_annotations = run_mer(sentence, filename)

    unchecked_annotations_list = []

    # Check if there are any annotations from MER
    if original_annotations:
        for i, annotation in enumerate(original_annotations):
            is_unique = True

            # Compare current annotation with every other annotation
            for j, other_annotation in enumerate(original_annotations):
                if i != j:  # Make sure not to compare the annotation with itself
                    # Check if the first or second value matches
                    if annotation[0] == other_annotation[0] or annotation[1] == other_annotation[1]:
                        is_unique = False
                        # If the current annotation has a longer fourth value, prefer it
                        if len(annotation[2]) > len(other_annotation[2]):
                            unchecked_annotations_list.append(annotation)
                        else:
                            unchecked_annotations_list.append(other_annotation)
                        break  # Stop checking further as we've found a match

            if is_unique:
                unchecked_annotations_list.append(annotation)

    else:
        return unchecked_annotations_list

    # Remove duplicates based on first and second values
    final_annotations_list = list(set(unchecked_annotations_list))

    return final_annotations_list
    
    

def divide_by_sentences(input_text):
    """Called by the create_dataset() function. Divides input text into sentences and returns them in a list of strings

    :param input_text (str): text to divide
    :return list: list of sentences (str)
    """

    nltk_path = os.path.join('..','nltk_data','tokenizers','punkt','english.pickle')
    tokenizer = nltk.data.load(nltk_path)
    sentences = []
    for sentence in tokenizer.tokenize(input_text):
        sentences.append(sentence)

    return sentences



def run_mer(input_text, filename):
    """Called by the get_annotations() function. Produces a list of annotations for the input text based on entity terms found
    in the lexicon files.
    
    :param input_text (str): input text with potential relevant entities
    :param filename (str): article identifier from which input text originates
    :return list: annotations for input_text
            annotation list example: [(81, 85, 'corn', http://purl.obolibrary.org/obo/NCBITaxon_381124, 'PL'),
                                    (98, 108, 'Firmicutes', http://purl.obolibrary.org/obo/NCBITaxon_1239, 'MO'),
                                    (172, 179, 'drought', 'ST')]
    """

    original_annotations = []
    excluded_sentences_path = os.path.join('..','..','corpus_data','excluded_sentences.txt')

    # Start annotation process
    for data_source in data_sources:

        results = []
        result = subprocess.run([f"./get_entities.sh '{input_text}' {data_source}"], capture_output=True, text=True, shell=True, encoding='utf-8')
        if result.stdout != '':
            result_string = result.stdout
            result_string = result_string.split('\n')
            results.append(result_string)

            if data_source == 'microorganisms':
                list1 = [annotation for annotation_list in results for annotation in annotation_list if annotation != '' and not re.search(r'^\s+$', annotation)]
            elif data_source == 'stress':
                list2 = [annotation for annotation_list in results for annotation in annotation_list if annotation != '' and not re.search(r'^\s+$', annotation)]
            elif data_source == 'plants':
                list3 = [annotation for annotation_list in results for annotation in annotation_list if annotation != '' and not re.search(r'^\s+$', annotation)]
        else:
            with open(excluded_sentences_path, 'a', encoding='utf-8') as excluded_sentences:
                excluded_sentences.write(f'[{filename}]|{input_text}\n')
            return original_annotations  # If input_text doesn't have all three types of entities, forgo annotation



    # Tag annotations based on type of entity
    for annotation_MO in list1: # Microorganisms

        class_index_1 = annotation_MO.split('\t')[0]
        class_index_2 = annotation_MO.split('\t')[1]
        class_name = annotation_MO.split('\t')[2]
        class_id =  annotation_MO.split('\t')[3]
        source_tag = 'MO'

        original_annotations.append((class_index_1, class_index_2, class_name, class_id, source_tag))
    
    for annotation_ST in list2: # Stress

        class_index_1 = annotation_ST.split('\t')[0]
        class_index_2 = annotation_ST.split('\t')[1]
        class_name = annotation_ST.split('\t')[2]
        class_id =  annotation_ST.split('\t')[3]
        source_tag = 'ST'

        original_annotations.append((class_index_1, class_index_2, class_name, class_id, source_tag))

    for annotation_PL in list3: # Plants
        
        class_index_1 = annotation_PL.split('\t')[0]
        class_index_2 = annotation_PL.split('\t')[1]
        class_name = annotation_PL.split('\t')[2]
        class_id =  annotation_PL.split('\t')[3]
        source_tag = 'PL'

        original_annotations.append((class_index_1, class_index_2, class_name, class_id, source_tag))

    return original_annotations # original_annotations == [] if input_text doesn't have all three entities




################################################
#         CREATING UNANNOTATED DATASET         #
################################################

def create_dataset_entry(filename, annotations, text, destination_path, annotations_path, seen_entries):
    """Called by the create_dataset() function. Creates an entry to be added to the unannotated dataset. 
    Format: [PMCID] | [MICROORGANISM] | [STRESS] | [PLANT] | [SENTENCE] | [RELATION]

    :param filename (str): file name, represented by the article's PMC ID
    :param annotations (list): annotations from MER
    :param text (str): input text
    :param destination_path (str): destination path for dataset file
    :param annotations_path (str): destination path for annotations files
    :param seen_entries (set): entries already added to dataset (prevents duplicates)
    :return (yield) dataset_entries_count: number of entries added to dataset in cycle
    """
    
    annotations_file = os.path.join(annotations_path,filename)

    dataset_entries_count = 0
    pmcid = filename.replace('.txt', '')
    MO_annotations = []
    ST_annotations = []
    PL_annotations = []

    for annotation in annotations:
        if annotation[4] == 'MO':
            MO_annotations.append(annotation)
        elif annotation[4] == 'ST':
            ST_annotations.append(annotation)
        elif annotation[4] == 'PL':
            PL_annotations.append(annotation)

    with open(annotations_file, 'a', encoding = 'utf-8') as annotations:

        with open(destination_path, 'a', encoding = 'utf-8') as dataset_file:
            sentence = text.strip()
            relation = 'YES'    # Assumes that every sentence with the three entity types represents a relation.
                                # Requires manual relation tagging ("YES" if it represents a relation, and "NO" if it doesn't)

            # Iterate over every type of annotation to get every possible entity combination
            for MO_annotation in MO_annotations:
                microorganism = MO_annotation[2]

                for ST_annotation in ST_annotations:
                    stress = ST_annotation[2]

                    for PL_annotation in PL_annotations:
                        plant = PL_annotation[2]

                        dataset_entry = f'{pmcid} | {microorganism} | {stress} | {plant} | {sentence} | {relation}'

                        if dataset_entry not in seen_entries:
                            try:
                                dataset_file.write(f'{dataset_entry}\n')
                                dataset_entries_count +=1
                                annotations.write(f'SENTENCE: {sentence}\nANNOTATIONS:\n{MO_annotation}\n{ST_annotation}\n{PL_annotation}\n----------\n')
                                seen_entries.add(dataset_entry)

                            except:
                                print(f"Error writing to dataset file!!!")
    
    yield dataset_entries_count
    yield seen_entries




def create_dataset(corpus_path, destination_path, annotations_path, abbreviations_dict, sorted_abbreviations, patterns):    # needs to be run from /bin/MER/
    """Called by the get_dataset_full() function. Creates a silver-standard, unannotated dataset file

    :param corpus_path (str): original corpus path
    :param destination_path (str): destination path for dataset file (.txt)
    :param annotations_path (str): destination path for annotations files
    :param abbreviations_dict (dict): dictionary mapping abbreviations (keys) to full taxon names (values)
    :param sorted_abbreviations (list): list of abbreviations sorted by length
    :param patterns (list): list of text patterns to match and edit text accordingly
    :return side effect: creates an annotation file for each abstract in the corpus
             annotation file example:

            81	85	corn	http://purl.obolibrary.org/obo/NCBITaxon_381124
            87	92	wheat	http://purl.obolibrary.org/obo/NCBITaxon_4565
            98	108	Firmicutes	http://purl.obolibrary.org/obo/NCBITaxon_1239 

    :return side effect: creates a silver standard, unannotated dataset file with the format 
            [PMCID] | [MICROORGANISM] | [STRESS] | [PLANT] | [SENTENCE] | [RELATION]
             dataset file example:

            87654567 | Promicromonospora | Salt | Cucumber | 'Previously, we observed the Burkholderia cepacia SE4, Promicromonospora sp. SE188 and A. calcoaceticus SE370 bacterial treatments promoted the plant growth and reduced the ABA content in salt and drought stress affected cucumber plants (Kang et al., 2014b).' | YES
            23456760 | Bacillus thuringiensis | Drought | Salvia | 'Lavadula demonstrated a greater benefit than Salvia to control drought stress when inoculated with B. thuringiensis.' | YES
            09877858 | Pseudomonas putida | Salt | Soybean | 'We found P. putida H-2-3 associated with soybean plants at drought or salt stress comforted to improve the plant growth by increasing or decreasing the endogenous SA level, respectively.' | YES
    """

    # Initialize number of files that produce no entries (to evaluate relevance of total articles in raw corpus)
    texts_no_entries = 0
    ids_no_entries = []
    seen_entries = set()

    # Initialize dataset entries to obtain the number of instances in final dataset
    dataset_entries_count = 0

    # Initialize amount of files that are being processed
    file_amount = 0

    for (dir_path, dir_names, file_names) in os.walk(corpus_path):

        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        for filename in file_names:                    
            file_amount +=1
            entries_created = False

            complete_filename = os.path.join(dir_path,filename)
            path_parts = os.path.split(dir_path)
            stress_part = os.path.split(path_parts[0])
            format = path_parts[1]
            stress = stress_part[1]
            annotations_directory = os.path.join(stress,format)
            annotations_destination = os.path.join(annotations_path,annotations_directory)

            text = open(complete_filename, 'r', encoding = 'utf-8')
            text = (text.readlines())
            if text == []:
                filename = complete_filename.replace('../../', '')
                os.system(f'rm {filename}')    # Removes file if it's empty
                print(f"!!!!\n{complete_filename.replace('../../', '')} has been ELIMINATED from corpus\n!!!!")
                continue    # Skips processing
            else:
                text = text[0]

            # Divide text into sentences for processing
            divided_text = divide_by_sentences(text)
            for sentence in divided_text:

                if not re.search(r'^\s+$', sentence) and not re.search(r'^Figure\s\d', sentence):
                    # Replace abbreviations in sentence
                    complete_sentence = replace_abbreviations_in_text(sentence, patterns, sorted_abbreviations, abbreviations_dict)

                    # Get all combinations of annotations for sentence
                    final_annotations_list = get_annotations(complete_sentence, filename)

                    # If annotations were produced, add original sentence and MER entities to unannotated dataset
                    if final_annotations_list != []:
                        dataset_path = os.path.join(destination_path,'SS_Dataset.txt')

                        if not os.path.exists(annotations_destination):
                            os.makedirs(annotations_destination)

                        result = create_dataset_entry(filename, final_annotations_list, complete_sentence, dataset_path, annotations_destination, seen_entries)
                        dataset_entries_count +=int(next(result))
                        seen_entries = next(result)
                        entries_created = True
            
            # If no dataset entries were produced from file
            if not entries_created:
                texts_no_entries +=1
                ids_no_entries.append(filename)

    
    print(f'Dataset is composed of {dataset_entries_count} entries.')
    print(f"Of {file_amount} files checked, {texts_no_entries} didn't produce any dataset entries.\n \
          Query relevance: {(1-(texts_no_entries/file_amount))*100} %")
    
    no_entries_path = os.path.join('..','..','dataset','articles_no_entries.txt')
    with open(no_entries_path, 'w', encoding = 'utf-8') as file:
        for id in ids_no_entries:
            file.write(f'{id}\n')
          

def get_dataset_full(corpus_path, dataset_file_path, annotations_directory):
    """Generates abbreviations dictionary and patterns for abstract and full text editing, then creates the untagged and
    unannotated dataset

    :param corpus_path (str): original corpus path
    :param dataset_file_path (str): destination path for dataset file (.txt)
    :param annotations_directory (str): destination path for annotations files
    :return side effect: .txt dataset, each entry with format [DOI] | [MICROORGANISM] | [STRESS] | [PLANT] | [TEXT] | [RELATION]
    """

    print("Generating abbreviations...")
    start_time = time.time() #--------------------------------------------------------------------------------- LOG: TIME

    # Get abbreviations dictionaries for microorganisms and plants and merge them into a single one
    MOs_path = os.path.join('data','microorganisms.txt')
    abbreviations_dict = generate_abbreviations(MOs_path)

    PLs_path = os.path.join('data','plants.txt')
    dict_to_merge = generate_abbreviations(PLs_path)
    abbreviations_dict.update(dict_to_merge)    # Final dictionary with all abbreviations

    print(f'RUNTIME: {time.time() - start_time:.1f} seconds') #----------------------------------------------- LOG: TIME


    # Sort abbreviations by full name length in descending order to handle nested abbreviations properly
    sorted_abbreviations = sorted(abbreviations_dict, key=lambda k: len(abbreviations_dict[k]), reverse=True)

    # Create patterns
    patterns = []
    for to_match in sorted_abbreviations:
        patterns.append(re.compile(fr'\b{re.escape(to_match)}\b(?=\W|$)'))
    
    create_dataset(corpus_path, dataset_file_path, annotations_directory, abbreviations_dict, sorted_abbreviations, patterns)






#####################
#        RUN        #
#####################

def main():
    """Creates a silver-standard unannotated dataset file

    :return: silver-standard unannotated dataset file (every instance is tagged "YES" for relation)
    """

    os.chdir('./bin/MER')
    start_time = time.time() #-------------------------------------------------------------------------------- LOG: TIME

    dataset_file_path = os.path.join('..','..','dataset')                       # '../../dataset'
    annotations_directory = os.path.join('..','..','corpus_data','annotations') # '../../corpus_data/annotations'
    articles_path = os.path.join('..','..','corpus_data','articles')            # '../../corpus_data/articles'
    get_dataset_full(articles_path, dataset_file_path, annotations_directory)

    print(f'Raw dataset has been created at {dataset_file_path.replace("../..", "")}')
    print(f'RUNTIME: {time.time() - start_time:.1f} seconds') #----------------------------------------------- LOG: TIME

    return


if __name__ == "__main__":
    main()
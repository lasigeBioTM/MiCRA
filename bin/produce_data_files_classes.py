import os
import re
import time
from owlready2 import get_ontology



def read_classes_into_array(file_path):
    """Reads the classes file line by line, strips newline characters and class names,
    and returns the IRIs as a list of strings
    
    :param file_path (str): path to file
    :return list: list of IRIs
    """

    lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip().split(" | ")[1] for line in file.readlines()]  # Strip newline characters and names

    return lines



def strip_label(label):
    """Cleans up labels by removing specific unwanted characters
    
    :param label (str): label 
    :return str: clean label
    """

    return str(label).replace("['", "").replace("']", "")



def start_process_owl_file(ontology, lines, labels_file, links_file, synonyms_file):
    """Takes a list of classes and iterates over the ontology, extracting labels, synonyms and IRIs
    for each matching class (also handles every subclass)
    
    :param ontology (str): ontology (.owl) file
    :param lines (list): list of strings (class IRIs)
    :param labels_file (str): path to labels file (.txt)
    :param links_file (str): path to links ([LABEL] [IRI]) file (.txt)
    :param synonyms_file (str): path to file where label and respective synonyms will be stored (.txt)
    :return side effect: creates labels file, synonyms file, and links file
    """

    ids_to_process = []

    # Iterate over all classes in the ontology
    for cls in ontology.classes():
        if cls.iri in lines:

            # Write class label and IRI to the output files
            labels_file.write(f"{strip_label(str(cls.label).lower())}\n")
            synonyms_file.write(f"{strip_label(str(cls.label).lower())}\n")
            links_file.write(f"{strip_label(str(cls.label).lower())}|{strip_label(cls.iri)}\n")
            ids_to_process.append(cls.iri)

            # Process and write synonyms
            for synonym in cls.hasExactSynonym:
                if (any(char.isdigit() for char in synonym) and ' ' not in synonym and len(synonym)<5 or synonym == ''):    # Check if synonym is a single word with numbers (ex: SA1) or doesn't exist
                    break
                else:
                    labels_file.write(f"{synonym.lower()}\n")
                    synonyms_file.write(f"{synonym.lower()}\n")
                    links_file.write(f"{synonym.lower()}|{cls.iri}\n")
            for synonym in cls.hasRelatedSynonym:
                if (any(char.isdigit() for char in synonym) and ' ' not in synonym and len(synonym)<5 or synonym == ''):    # Check if synonym is a single word with numbers (ex: SA1) or doesn't exist
                    break
                else:
                    labels_file.write(f"{synonym.lower()}\n")
                    synonyms_file.write(f"{synonym.lower()}\n")
                    links_file.write(f"{synonym.lower()}|{cls.iri}\n")
        
            synonyms_file.write("-\n")
        

    # Recursively process subclasses of identified classes        
    if len(ids_to_process) > 0:
        process_owl_file(ontology, ids_to_process, labels_file,links_file, synonyms_file)



def process_owl_file(ontology, lines, labels_file, links_file, synonyms_file):
    """Recursively processes subclasses of the classes identified in 'start_process_owl_file'
    
    :param ontology (str): ontology (.owl) file
    :param lines (list): list of strings (class IRIs)
    :param labels_file (str): path to labels file (.txt)
    :param links_file (str): path to links ([LABEL] [IRI]) file (.txt)
    :param synonyms_file (str): path to file where label and respective synonyms will be stored (.txt)
    :return side effect: creates labels file, synonyms file, and links file
    """
    
    no_mappings = set()
    ids_to_process = []
    for id in lines:
        # Search for the class by IRI
        cls = ontology.search_one(iri=id)
        sub_ontology = ontology.search(subclass_of = cls)
        if len(sub_ontology) > 0:
            for sub_cls in sub_ontology:
                if sub_cls.iri == id:
                    continue
                
                # Check if the class has certain mappings (e.g., hasDbXref)
                has_mappings = False
                if hasattr(sub_cls, "oboInOwl_hasDbXref"):
                    has_mappings = True
                    continue

                # If no mappings were found, add to no_mappings
                if not has_mappings:
                    no_mappings.add(str(sub_cls).replace('obo.', ''))

                # Write subclass label and IRI to the output files
                labels_file.write(f"{strip_label(str(sub_cls.label).lower())}\n")
                synonyms_file.write(f"{strip_label(str(sub_cls.label).lower())}\n")
                links_file.write(f"{strip_label(str(sub_cls.label).lower())}|{strip_label(sub_cls.iri)}\n")
                ids_to_process.append(sub_cls.iri)

                # Process and write synonyms
                for synonym in sub_cls.hasExactSynonym:
                    if (any(char.isdigit() for char in synonym) and ' ' not in synonym and len(synonym)<5) or synonym == '':    # Check if synonym is a single word with numbers (ex: SA1) or doesn't exist
                        break
                    else:
                        labels_file.write(f"{synonym.lower()}\n")
                        synonyms_file.write(f"{synonym.lower()}\n")
                        links_file.write(f"{synonym.lower()}|{sub_cls.iri}\n")
                for synonym in sub_cls.hasRelatedSynonym:
                    if (any(char.isdigit() for char in synonym) and ' ' not in synonym and len(synonym)<5) or synonym == '':    # Check if synonym is a single word with numbers (ex: SA1) or doesn't exist
                        break
                    else:
                        labels_file.write(f"{synonym.lower()}\n")
                        synonyms_file.write(f"{synonym.lower()}\n")
                        links_file.write(f"{synonym.lower()}|{sub_cls.iri}\n")
                    
                synonyms_file.write("-\n")
    

    print(f'Number of classes with no mappings: {len(no_mappings)}') #--------------------------------------------------- LOG: INFO
    print(f'Class IDs:')
    print('; '.join(no_mappings)) #--------------------------------------------------------------------------------- LOG: INFO



def edit_file(original_file, new_file):
    """Takes a text file and produces a new file without duplicates and unwanted characters
    or lines, and added relevant entries

    :param original_file (str): path to original file
    :param new_file (str): path to new file
    :return side effect: creates file with unique edited entries plus additional ones
    """

    lines_seen = set()  # Holds lines already seen

    with open(original_file, 'r', encoding='utf-8') as input_file:
        lines = input_file.readlines()

        with open(new_file, 'w', encoding='utf-8') as output_file:
            for line in lines:

                # Remove unwanted characters
                line = re.sub("^'", '', line)
                line = re.sub("'$", '', line)
                line = re.sub(r'\[', '', line)
                line = re.sub(r'\]', '', line)
                line = re.sub(r'\(', '', line)
                line = re.sub(r'\)', '', line)

                # If line is a separator, write it to output file
                if line == '-\n':
                    output_file.write(line)

                # Only process non-empty lines that haven't been seen before
                elif line not in lines_seen and line != '' and not re.search(r'\(nom\. inval\.\)$', line, re.IGNORECASE):

                    # Include common names without the "common" prefix
                    if re.search('^common', line, re.IGNORECASE):
                        no_prefix = line.replace('common ', '')
                        if no_prefix not in lines_seen:
                            lines_seen.add(no_prefix)
                            output_file.write(f'{no_prefix}')

                    # Include names without authors &/or entry year
                    if re.search(r"\(", line):
                        no_author_year = re.sub(r" \((.*)\|", '|', line)
                        if no_author_year not in lines_seen:
                            lines_seen.add(no_author_year)
                            output_file.write(f'{no_author_year}')

                    # Extract names in between " "
                    if re.search('"(.*)"', line):
                        no_accents = re.search('"(.*)"', line).group(1)
                        if no_accents not in lines_seen:
                            lines_seen.add(no_accents)
                            output_file.write(f'{no_accents}')

                    # Skip irrelevant terms
                    if re.search('^algae$', line, re.IGNORECASE) or \
                        re.search('^plants$', line, re.IGNORECASE) or \
                        re.search('^phyla$', line, re.IGNORECASE) or \
                        re.search('^microbiota$', line, re.IGNORECASE) or \
                        re.search('^archaea$', line, re.IGNORECASE) or \
                        re.search('^eubacteria$', line, re.IGNORECASE) or \
                        re.search('^bacteria$', line, re.IGNORECASE) or \
                        re.search('^rhizobacteria$', line, re.IGNORECASE) or \
                        re.search('^rhizobacterium$', line, re.IGNORECASE) or \
                        re.search('^bacterium$', line, re.IGNORECASE) or \
                        re.search('^viruses$', line, re.IGNORECASE) or \
                        re.search('^virus$', line, re.IGNORECASE) or \
                        re.search('^subgroup A$', line, re.IGNORECASE) or \
                        re.search('^subgroup B$', line, re.IGNORECASE) or \
                        re.search('^subgroup C$', line, re.IGNORECASE) or \
                        re.search('^ammonia$', line, re.IGNORECASE) or \
                        re.search('^codon$', line, re.IGNORECASE) or \
                        re.search('^cotyledon$', line, re.IGNORECASE) or \
                        re.search('^glycine$', line, re.IGNORECASE) or \
                        re.search('^endophyticum bacterium$', line, re.IGNORECASE) or \
                        re.search('^vascular plants$', line, re.IGNORECASE) or \
                        re.search('^agent', line, re.IGNORECASE) or \
                        re.search('unclassified', line, re.IGNORECASE) or \
                        re.search('unidentified', line, re.IGNORECASE) or \
                        re.search('environmental', line, re.IGNORECASE) or \
                        re.search('uncultured', line, re.IGNORECASE) or \
                        re.search('unknown', line, re.IGNORECASE):
                        continue

                    # Add line to seen list and write it to file
                    lines_seen.add(line)
                    output_file.write(f'{line}')

    
    output_file.close()
    os.remove(original_file)



def edit_labels_file():
    """Takes the temporary labels file, edits it and creates the final version

    :return str: name of the new labels file
    :return side effect: creates new file with unique edited entries and additional ones
    """

    input_file = file_labels_path
    output_file = input_file.replace('_templabels', '')
    edit_file(input_file, output_file)

    return output_file


def edit_synonyms_file():
    """Takes the temporary synonyms file, edits it and creates the final version

    :return str: name of the new synonyms file
    :return side effect: creates new file with unique edited entries and additional ones
    """

    input_file = file_synonyms_path
    output_file = input_file.replace('temp', '')
    edit_file(input_file, output_file)

    return output_file



def edit_links_file():
    """Takes the temporary links file, edits it and creates the final version

    :return str: name of the new links file
    :return side effect: creates new file with unique edited entries and additional ones
    """

    input_file = file_links_path
    output_file = input_file.replace('temp', 'temp2')
    edit_file(input_file, output_file)

    return output_file



def replace_text(file_path, replacement_list):
    """Replaces text in a .txt file without the need to overwrite it entirely or create a new file

    :param file_path (str): path to .txt file
    :param replacement_list (list): list of tuples with the format (original_text, replacement)
    :return side effect: applies changes to given .txt file
    """

    with open(file_path, 'r+', encoding='utf-8') as f: 
        file_content = f.read()
        
        # Perform all replacements
        for search_text, replace_text in replacement_list:
            # Replace the patterns in the file content
            file_content = re.sub(search_text, replace_text, file_content)
        
        # Move the file pointer to the beginning
        f.seek(0)
        
        # Write the modified content once
        f.write(file_content)
        
        # Truncate the file to remove leftover content from the previous version
        f.truncate()



def final_editing_microorganisms():
    """Manual editing of dataset based on perceived missing values (run only for microorganisms data files)

    :return side effect: applies changes to microorganisms data files
    """

    # Handling labels file: only need to add the extra terms (order is irrelevant)
    with open(output_labels_file, 'a', encoding='utf-8') as labels_file:
        labels_file.write(f"bacillus megaterium\nglomus etunicatum\nturnip mosaic potyvirus\nsaccharibacteria\npseudomonas stutzeri\namf\nrhizoglomus irregularis")

    # Handling synonyms file: add extra terms near synonyms (order is IMPORTANT)
    replace_text(output_synonyms_file,[
        ("priestia megaterium", f"priestia megaterium\nbacillus megaterium"),
        ("glomeromycotina",f"glomeromycotina\namf"),
        ("glomus intraradices",f"glomus intraradices\nrhizoglomus irregularis"),
        ("stutzerimonas stutzeri",f"stutzerimonas stutzeri\npseudomonas stutzeri"),
        ("entrophospora etunicata", f"entrophospora etunicata\nglomus etunicatum"),
        ("turnip mosaic potyvirus tumv", f"turnip mosaic potyvirus tumv\nturnip mosaic potyvirus"),
        ("candidatus saccharibacteria", f"candidatus saccharibacteria\nsaccharibacteria"),
        ])

    # Handling links file: add extra terms with corresponding links from linked synonym (order is irrelevant)
    with open(output_links_file, 'a', encoding='utf-8') as links_file:
        links_file.write(
        f"bacillus megaterium|http://purl.obolibrary.org/obo/NCBITaxon_1404"
        f"amf|http://purl.obolibrary.org/obo/NCBITaxon_214504"
        f"rhizoglomus irregularis|http://purl.obolibrary.org/obo/NCBITaxon_4876"
        f"pseudomonas stutzeri|http://purl.obolibrary.org/obo/NCBITaxon_316"
        f"glomus etunicatum|http://purl.obolibrary.org/obo/NCBITaxon_937382"
        f"turnip mosaic potyvirus|http://purl.obolibrary.org/obo/NCBITaxon_12230"
        f"saccharibacteria|http://purl.obolibrary.org/obo/NCBITaxon_95818"
        )



def final_editing_plants():
    """Manual editing of dataset based on perceived missing values (run only for plants data files)

    :return side effect: applies changes to plants data files
    """

    # Handling labels file: only need to add the extra terms (order is irrelevant)
    with open(output_labels_file, 'a', encoding='utf-8') as labels_file:
        labels_file.write(f"pepper\n"
                          "bell pepper\n"
                          "red peppers\n"
                          "millet\n"
                          "sunflower\n"
                          "groundnut\n"
                          "groundnuts\n"
                          "rapeseed\n"
                          "mungbean\n"
                          "mung bean\n"
                          "moong\n"
                          "great millet\n"
                          "grapevine\n"
                          "grape\n"
                          "grapes\n"
                          "french lavender\n"
                          "jujube\n"
                          "squash\n"
                          "common bean\n"
                          "beans\n"
                          "bean\n"
                          "lavandula spica\n"
                          "lettuce")

    # Handling synonyms file: add extra terms near synonyms (order is IMPORTANT)
    replace_text(output_synonyms_file,[
        ("capsicum annuum", f"capsicum annuum\npepper\nbell pepper"),
        ("capsicum annuum var. annuum",f"capsicum annuum var. annuum\nred peppers"),
        ("poaceae", f"poaceae\nmillet"),
        ("helianthus annuus", f"helianthus annuus\nsunflower"),
        ("arachis hypogaea",f"arachis hypogaea\ngroundnut\ngroundnuts"),
        ("brassica napus", f"brassica napus\nrapeseed"),
        ("vigna radiata", f"vigna radiata\nmung bean\nmoong\nmungbean"),
        ("sorghum",f"sorghum\ngreat millet"),
        ("vitis vinifera", f"vitis vinifera\ngrapevine\ngrapes\ngrape"),
        ("lavandula dentata", f"lavandula dentata\nFrench lavender"),
        ("zizyphus jujuba", f"zizyphus jujuba\njujube"),
        ("galega officinalis",f"galega officinalis\ngoat's rue"),
        ("cucurbita", f"cucurbita\nsquash"),
        ("phaseolus vulgaris",f"phaseolus vulgaris\ncommon bean\nbeans\nbean"),
        ("lavandula latifolia", f"lavandula latifolia\nlavandula spica"),
        ("lactuca sativa", f"lactuca sativa\nlettuce")
        ])

    # Handling links file: add extra terms with corresponding links from linked synonym (order is irrelevant)
    with open(output_links_file, 'a', encoding='utf-8') as links_file:
        links_file.write(
        f"pepper|http://purl.obolibrary.org/obo/NCBITaxon_4072\n"
        f"bell pepper|http://purl.obolibrary.org/obo/NCBITaxon_4072\n"
        f"red peppers|http://purl.obolibrary.org/obo/NCBITaxon_40321\n"
        f"millet|http://purl.obolibrary.org/obo/NCBITaxon_4479\n"
        f"sunflower|http://purl.obolibrary.org/obo/NCBITaxon_4232\n"
        f"groundnut|http://purl.obolibrary.org/obo/NCBITaxon_3818\n"
        f"groundnuts|http://purl.obolibrary.org/obo/NCBITaxon_3818\n"
        f"rapeseeed|http://purl.obolibrary.org/obo/NCBITaxon_3708\n"
        f"mung bean|http://purl.obolibrary.org/obo/NCBITaxon_157791\n"
        f"mungbean|http://purl.obolibrary.org/obo/NCBITaxon_157791\n"
        f"moong|http://purl.obolibrary.org/obo/NCBITaxon_157791\n"
        f"great millet|http://purl.obolibrary.org/obo/NCBITaxon_4557\n"
        f"grapevine|http://purl.obolibrary.org/obo/NCBITaxon_29760\n"
        f"grape|http://purl.obolibrary.org/obo/NCBITaxon_29760\n"
        f"grapes|http://purl.obolibrary.org/obo/NCBITaxon_29760\n"
        f"lavandula dentata|http://purl.obolibrary.org/obo/NCBITaxon_1441374\n"
        f"jujube|http://purl.obolibrary.org/obo/NCBITaxon_326968\n"
        f"goat's rue|http://purl.obolibrary.org/obo/NCBITaxon_47101\n"
        f"squash|http://purl.obolibrary.org/obo/NCBITaxon_3660\n"
        f"common bean|http://purl.obolibrary.org/obo/NCBITaxon_3885\n"
        f"lavandula spica|http://purl.obolibrary.org/obo/NCBITaxon_39331\n"
        f"beans|http://purl.obolibrary.org/obo/NCBITaxon_3885\n"
        f"bean|http://purl.obolibrary.org/obo/NCBITaxon_3885\n"
        f"lettuce|http://purl.obolibrary.org/obo/NCBITaxon_4236\n"
        )



def split_labels_into_files(labels, filename):
    """Divides the labels found into different files according to the number of words and uniqueness
    
    :param labels (str): path to labels file (.txt)
    :return side effect: creates 4 files, each with different length labels
    """

    word1_file = os.path.join('bin','MER','data',f'{filename}_word1.txt')
    word2_file = os.path.join('bin','MER','data',f'{filename}_word2.txt')
    words_file = os.path.join('bin','MER','data',f'{filename}_words.txt')
    words2_file = os.path.join('bin','MER','data',f'{filename}_words2.txt')

    with open(word1_file, 'w', encoding='utf-8') as single_file, \
         open(word2_file, 'w', encoding='utf-8') as two_word_file, \
         open(words_file, 'w', encoding='utf-8') as multi_word_file, \
         open(words2_file, 'w', encoding='utf-8') as unique_two_word_file:

        two_word_seen = set()

        # Process each label from the input file
        with open(labels, 'r', encoding='utf-8') as file:
            for line in file:
                words = line.strip().split()

                if len(words) == 1:
                    # Single word
                    single_file.write(line.lower())
                
                elif len(words) == 2:
                    # Two-word combination
                    two_word_file.write(line.lower())
                    
                    # Process unique two-word combinations
                    combination = tuple(sorted(words))
                    if combination not in two_word_seen:
                        unique_two_word_file.write(line.lower())
                        two_word_seen.add(combination)
                
                elif len(words) > 2:
                    # Multiple words (3 or more)
                    multi_word_file.write(line.lower())



def tsv_links_file(links_file):
    """Writes every entry of the links file to a .tsv for matching with get_entities.sh
    
    :param links_file (str): labels and IDs file (.txt)
    :return side effect: creates final labels and IDs file (.tsv)
    """

    links_name = links_file.replace('_temp2links.txt','')
    with open(links_file,'r', encoding='utf8') as input_file:
        lines = input_file.readlines()
        with open (f'{links_name}_links.tsv', 'w', encoding='utf8') as output_file:
            for line in lines:
                label = line.split('|')[0].lower()
                id = line.split('|')[1]
                entity = (f'{label}\t{id}')
                output_file.write(entity)
    
    os.remove(links_file)






print("---------------------------\n  CREATING LEXICON FILES\n---------------------------")        

     
#########################################################
#   HANDLE SPECIFIC CLASSES FILES FOR EACH DATA TYPE    #
#########################################################

MER_data_path = os.path.join('bin','MER','data')

os.makedirs(MER_data_path, exist_ok=True) # dir for lexicon text files

# Load the ontology
start_time = time.time() #----------------------------------------------------------------------------------------------- LOG: TIME
ontology_path = os.path.join('ncbitaxon.owl')               ### CHANGEABLE: Ontology file you're using ###
ontology = get_ontology(ontology_path).load()
end_time = time.time() #------------------------------------------------------------------------------------------------- LOG: TIME
print(f'\nLoading ontology runtime: {end_time - start_time:8.1f} seconds\n----------------------------------------') #--- LOG: INFO

data_sources = ['microorganisms', 'plants']         # Stress lexicon files were manually created

start_time = time.time() #----------------------------------------------------------------------------------------------- LOG: TIME

for data_type in data_sources:

    print(f'\n** {data_type.title()} lexicon data **\n')

    classes_path = os.path.join('.','bin',f'classes_{data_type}.txt')     ### CHANGEABLE: Classes files template name ###
    lines = read_classes_into_array(classes_path)  

    # Paths to files
    filename = classes_path.replace("./bin/classes_","").replace(".txt","")
    file_labels_path = os.path.join('.','bin','MER','data',f'{filename}_templabels.txt')
    file_links_path = os.path.join('.','bin','MER','data',f'{filename}_templinks.txt')
    file_synonyms_path = os.path.join('.','bin','MER','data',f'{filename}_tempsynonyms.txt')

    # Open output files for writing
    labels_file = open(file_labels_path, 'w', encoding='utf-8')
    links_file = open(file_links_path, 'w', encoding='utf-8')
    synonyms_file = open(file_synonyms_path, 'w', encoding='utf-8')

    # Process the ontology file and remove duplicates from resulting synonyms file
    start_process_owl_file(ontology, lines, labels_file, links_file, synonyms_file)
    output_labels_file = edit_labels_file()
    output_synonyms_file = edit_synonyms_file()
    output_links_file = edit_links_file()

    if data_type == 'microorganisms':       # Only microorganisms files are subjected to this step
        final_editing_microorganisms()
        
    if data_type == 'plants':               # Only plants files are subjected to this step
        final_editing_plants()

    # Split the labels file into the required files
    split_labels_into_files(output_labels_file, filename)
    tsv_links_file(output_links_file)

    labels_file.close()
    links_file.close()


print(f"\nLexicon files have been created at bin/MER/data")

end_time = time.time() #----------------------------------------------------------------------------------------------- LOG: TIME

print(f'RUNTIME: {end_time - start_time:8.1f} seconds\n----------------------------------------') #-------------------- LOG: INFO
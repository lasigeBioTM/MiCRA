import os
import re
import time


#########################################
#       GET PMCIDs FOR EACH STRESS      #
#########################################

def parse_synonyms_file(file_path):
    """Called by the get_pmcids_list() function. Reads and parses synonyms file, creating a dictionary
    mapping synonyms to the respective main term
    {'drought': ['dessication', 'water deficit', ...], ...}

    :param file_path (str): path to synonyms file
    :return dict: dictionary mapping synonyms to the respective main term
    """

    with open(file_path, 'r', encoding = 'utf-8') as file:
        synonyms_mapping = {}
        main_term = None
        synonyms = []

        for line in file:
            line = line.strip()  # Remove leading/trailing whitespaces

            if line == '-':  # If line is '-', reset for the next block
                if main_term and synonyms:
                    synonyms_mapping[main_term] = synonyms
                main_term = None
                synonyms = []

            elif re.search(r'\S\sx\s\S', line) or re.search(r'hybrid',line): # Hybrids won't be considered for synonym mapping (ex: Magnolia baillonii x Magnolia champaca)
                continue

            elif not main_term:  # The first line before '-' is the main term
                main_term = line

            else:  # Following lines until '-' are synonyms
                synonyms.append(line)

        # Add the last main term and its synonyms after exiting the loop
        if main_term and synonyms:
            synonyms_mapping[main_term] = synonyms

    return synonyms_mapping



def get_pmcids_list(file_path):
    """Uses a PubMed Central query to obtain PMCIDs of articles related to microbe-related plant stress tolerance,
    creating a .txt file of PMCIDs for each stress term and its synonyms in MER stress lexicon.

    :param file_path (str): destination path to file content
    :return side effect: .txt files with PMCIDs for each stress term found in bin/MER/data/stress.txt
    """

    # Get all terms from MER stress lexicon
    stress_synonyms_path = os.path.join('bin','MER','data','stress_synonyms.txt')
    stress_synonyms_mapping = parse_synonyms_file(stress_synonyms_path)                

    # Define keywords for querying    # ----------------------------------------------------------- CHANGEABLE
    ### ATTENTION:'AND' and 'OR' statements MUST be written inside the same string
    query_keywords = [
    "((microb*[All Fields]) OR (microorganism[All Fields] OR (Microbial Interactions[MeSH]) NOT (gut microbiome[All Fields])))",
    "((plant stress[All Fields]) OR (plant abiotic stress[All Fields]) OR (Stress, Physiological[MeSH]))",
    "((toleran*[All Fields] OR resilien*[All Fields]) OR (Plant Roots/microbiology[MeSH] OR Plant Shoots/microbiology[MeSH]) NOT (drug tolerance[All Fields]))"
    ]   

    print(f'QUERY KEYWORDS: [stress type] + {(" + ".join(query_keywords))}\n-----------------------------------------')
    
    # PubMed Central query for articles regarding microbe-mediated plant tolerance to each stress on our stress list
    for key, value in stress_synonyms_mapping.items():
        
        filename = 'tempfile_pmcids.xml'
        stress_terms_ids = []
        
        # Replace blank spaces with '%20' for HTML reading
        for i in range(0, len(query_keywords)):
            if ' ' in query_keywords[i]:
                query_keywords[i] = query_keywords[i].replace(' ', '%20')

        # Add key term to list of stress types that will be queried
        value.append(key)

        # Iterate through every stress type in list for querying
        for stress_type in value:
            if ' ' in stress_type:
                stress_type = stress_type.replace(' ', '%20')

            keywords = "+AND+".join(query_keywords)

            # Query format: {stress_type} plant microbe tolerance within the last 8 years
            os.system('curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=' + f'{stress_type}+AND+{keywords}&reldate=2922&datetype=edat&sort=relevance&retmax=150&retmode=xml" >> {filename}')

            exit_file = open(filename, 'r', encoding = 'utf-8')
            list_ids = exit_file.read().split('<IdList>')[-1].split('</IdList>')[0].split('\n')[1:-1]
            list_ids = [x.strip('</Id>') for x in list_ids]
            stress_terms_ids = stress_terms_ids + list_ids
            
        unique_ids = set(stress_terms_ids)

        # Get unique PMCIDs for each main stress term
        unique_ids_path = os.path.join(file_path,f'PMCids_{key}.txt')
        with open(unique_ids_path, 'w', encoding = 'utf-8') as f:
            f.write("\n".join(unique_ids))

        f.close()
        exit_file.close()

        print(f'{len(unique_ids)} PMC IDs retrieved for {key} stress.')

        # Remove raw extracted file
        os.system(f'rm {filename}')

    return stress_synonyms_mapping






#####################
#        RUN        #
#####################

def main():
    """Creates a directory with a .txt file of PMCIDs for each stress term in MER stress lexicon

    :return: directory with a .txt file of PMCIDs for each stress term in MER stress lexicon
    """

    start_time = time.time() #-------------------------------------------------------------------------------- LOG: TIME
    os.system('mkdir -p corpus_data/pmcid_files || true') # dir for PMCID text files
    print("-----------------------------------------\nRETRIEVING PMC IDs FOR EACH STRESS TYPE")
    destination_path = os.path.join('corpus_data','pmcid_files')
    get_pmcids_list(destination_path)
    print(f'-----------------------------------------\n')
    print(f'RUNTIME: {time.time() - start_time:.1f} seconds') #----------------------------------------------- LOG: TIME

    return


if __name__ == "__main__":
    main()

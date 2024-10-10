import os
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

    with open(file_path, 'r') as file:
        stress_mapping = {}
        main_term = None
        synonyms = []

        for line in file:
            line = line.strip()  # Remove leading/trailing whitespaces

            if line == '-':  # If line is '-', reset for the next block
                if main_term and synonyms:
                    stress_mapping[main_term] = synonyms
                    main_term = None
                    synonyms = []

            elif not main_term:  # The first line before '-' is the main term
                main_term = line
            else:  # Following lines until '-' are synonyms
                synonyms.append(line)

        # Add the last main term and its synonyms after exiting the loop
        if main_term and synonyms:
            stress_mapping[main_term] = synonyms

    return stress_mapping



def get_pmcids_list(file_path):
    """Uses a PubMed Central query to obtain PMCIDs of articles related to microbe-related plant stress tolerance,
    creating a .txt file of PMCIDs for each stress term and its synonyms in MER stress lexicon.

    :param file_path (str): destination path to file content
    :return side effect: .txt files with PMCIDs for each stress term found in bin/MER/data/stress.txt
    """

    # Get all terms from MER stress lexicon
    stress_synonyms_mapping = parse_synonyms_file('./bin/MER/data/stress_synonyms.txt')                

    # Define keywords for querying    # ----------------------------------------------------------- CHANGEABLE
    ### ATTENTION:'AND' and 'OR' statements MUST be written inside the same string
    #### Ex: "plant stress AND tolerance" instead of "plant stress" AND "tolerance"
    query_keywords = ["microbe OR microorganism", "plant stress", "tolerance"]

    print(f'QUERY KEYWORDS: [stress type] + {(" + ".join(query_keywords)).strip('"')}\n-----------------------------------------')
    
    # PubMed Central query for articles regarding microbe-mediated plant tolerance to each stress on our stress list
    for key, value in stress_synonyms_mapping.items():
        
        filename = f'tempfile_pmcids.xml'
        stress_terms_ids = []
        
        # Replace blank spaces with '%20' for HTML reading
        for i in range(0, len(query_keywords) -1):
            if ' ' in query_keywords[i]:
                query_keywords[i] = query_keywords[i].replace(' ', '%20')

        # Add key term to list of stress types that will be queried
        value.append(key)

        # Iterate through every stress type in list for querying
        for stress_type in value:
            if ' ' in stress_type:
                stress_type = stress_type.replace(' ', '%20')
        
            
            # Query format: {stress_type} plant microbe tolerance AND English[Language]
            os.system('curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=' + f'{stress_type}+{query_keywords[0]}+AND+{query_keywords[1]}+AND+{query_keywords[2]}+AND+English[Language]&reldate=1825&datetype=edat&retmax=1000&retmode=xml" >> {filename}')

            exit_file = open(filename, 'r', encoding = 'utf-8')
            list_ids = exit_file.read().split('<IdList>')[-1].split('</IdList>')[0].split('\n')[1:-1]
            list_ids = [x.strip('</Id>') for x in list_ids]
            stress_terms_ids = stress_terms_ids + list_ids
            
        unique_ids = set(stress_terms_ids)

        # 
        with open(f'{file_path}/PMCids_{key}.txt', 'w') as f:
            f.write(f'{"\n".join(unique_ids)}')

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

    :return side effect: directory with a .txt file of PMCIDs for each stress term in MER stress lexicon
    """

    start_time = time.time() #-------------------------------------------------------------------------------- LOG: TIME
    os.system('mkdir -p corpus_data/pmcid_files || true') # dir for PMCID text files
    print("-----------------------------------------\nRETRIEVING PMC IDs FOR EACH STRESS TYPE")
    get_pmcids_list("./corpus_data/pmcid_files")
    print(f'-----------------------------------------\n')
    print(f'RUNTIME: {time.time() - start_time:.1f} seconds') #----------------------------------------------- LOG: TIME

    return


if __name__ == "__main__":
    main()

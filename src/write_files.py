import os
import re
import subprocess
import xml.etree.ElementTree as ET
import time


file_writing_runtimes = []

##################################
#       CREATE RAW CORPUS        #
##################################

def write(output_path):
    """Creates two files for each article, one containing abstract content and another containing full-text
    content, and groups them in abstract and full-text folders for each stress type.

    :param output_path (str): destination path for abstract and full-text files
    :return side effect: creates a file for each retrieved abstract or full-text
    """
    
    print("-----------------------------------------\n    CORPUS CREATION INITIATED\n-----------------------------------------")
            
    # Iterate over files in corpus_data/pmcid_files
    pmc_dict = {}

    for (dir_path, dir_names, file_names) in os.walk("./corpus_data/pmcid_files"):
        if file_names == []:
            print("No files were found in corpus_data/pmcid_files!")
            return
        
        for file in file_names:
            # Construct the full path to the file
            file_path = os.path.join("./corpus_data/pmcid_files", file)
            
            pmcids_list = []
            stress = os.path.basename(file).split('_')[-1].split('.')[0]

            with open(file_path, "r") as pmcids_file:
                for x in pmcids_file.readlines():
                    pmcids_list.append(x.strip('\n'))
                if len(pmcids_list) != 0:
                    print(f"File {file} exists. PMC IDs successfully retrieved.")
                else:
                    print(f"We were unable to retrieve PMC IDs from {file_path}. Please check file.")
            
            pmc_dict[stress] = pmcids_list
        

    # pmc_dict is a dictionary containing the Pubmed Central IDs of articles with microbiome relations to
    # plant stress in the format {stress_A: [pmcid1, pmcid2,...], stress_B: [pmcid3, pmcid4,...], ...}
    

    for stress, id_list in pmc_dict.items():

        # Create directories if they don't exist yet
        body_path = f'{output_path}/{stress}/fulltexts'
        abstract_path = f'{output_path}/{stress}/abstracts'
        if not os.path.isdir(f'{output_path}/{stress}'):
            os.makedirs(body_path)
        if not os.path.isdir(abstract_path):
            os.mkdir(abstract_path)

        for pmcid in id_list:        
            os.system('curl -s --max-time 30 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=' + 
                pmcid + f'&rettype=fulltext&retmode=xml" > abstract.xml') # Maximum connection time: 30 seconds
        
            write_file(pmcid, abstract_path, "abstract")
            write_file(pmcid, body_path, "body")
    
    os.system('rm abstract.xml')

    print(f"\nCorpus has been created at {output_path}. \n-----------------------------------------")
    return



def write_file(pmcid, destination_path, objective):
    """Called by the write() function. Extracts the abstract and body from the full-text .xml
    file corresponding to each article.

    :param pmcid (str): PMC ID
    :param destination_path (str): destination path
    :param objective (str): what to retrieve (body or abstract)
    :return side effect: .txt file for each retrieved full-text body or abstract
    """

    start_time = time.time() #----------------------------------------------------------------------------------------------- LOG: TIME
    presence = subprocess.Popen(f"grep -q '<%s>' 'abstract.xml'" % objective, shell = True)
    return_code = presence.wait()
    if return_code != 1:
        
        mytree = ET.parse(f'abstract.xml')
        myroot = mytree.getroot()
        node = myroot.find('.//%s' % objective)
        file = open(destination_path + '/' + pmcid, "w")
        for line in node:
            txt_line = ET.tostring(line, encoding='unicode', method='xml')
            edited_line = edit_text(txt_line)
            if edit_text != '':         # If line isn't Null (doesn't contain a table), writes to file
                final_line = edited_line.replace('\n', ' ')
                file.write(final_line)

        file.close()
        
    file_writing_runtimes.append(time.time() - start_time)
    return



def edit_text(line):
    """Called by the write_file() function. Removes unwanted characters for each provided line.

    :param line (str): unedited line from an article's body or abstract
    :return str: original line post-editing
    """

    if "table-wrap" not in line:                # If the line does not contain a table, text is edited
        line = re.sub(r'<xref.+?xref>', ' (reference)', line)
        line = re.sub(r'<.+?>', '', line)
        line = re.sub(']','', line)
        line = re.sub(r'\[','', line)
        line = re.sub(r'\)','', line)     
        line = re.sub(r'\(','', line)   
        line = re.sub(r'\'','', line)
        line = re.sub(r'\"','', line)
        line = re.sub('&gt','', line)
        line = re.sub('&#x', '', line)
        line = re.sub("a.k.a.", 'a.k.a', line)
        new_line = line
    
    else:
        new_line = ''                           # If the line contains a table, the new line is Null
    

    return new_line






#####################
#        RUN        #
#####################

def main():
    """Creates a directory with a .txt file of PMCIDs for each stress term in MER stress lexicon

    :return: directory with a .txt file of PMCIDs for each stress term in MER stress lexicon
    """

    start_time = time.time() #------------------------------------------------------------------------------------------ LOG: TIME   
    
    os.system('mkdir -p RAW_CORPUS || true') # Main dir for edited text corpus (to use for MER)
    write('./RAW_CORPUS')

    print(f"RAW CORPUS CREATION PROCESS RUNTIME:  {time.time() - start_time:.1f} seconds") #----------------------------- LOG: TIME

    average_file_writing_runtime = sum(file_writing_runtimes)/len(file_writing_runtimes)
    print(f"\nAVERAGE FILE WRITING RUNTIME: {average_file_writing_runtime} seconds")
    return


if __name__ == "__main__":
    main()
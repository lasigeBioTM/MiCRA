import os
import subprocess
import sys
from polyglot.detect import Detector


#### ORIGINAL ABSTRACTS ####

def get_pmc_ids_list(stress_list):
    """Creates a list of type [[stress_type1, pmc_ID1, pmc_ID2, ...], [stress_type2, pmc_ID3, pmc_ID4, ...], ...]

    :param stress_list: file with different types of abiotic stress in plants
    :return: list of lists with the ids of PubMed Central (PMC) articles with microbiome
             relations to plant stress in the format [[stress type, pmc_ID1], [stress type, pmc_ID2], ...]
    """

    pmc_list = []

    for stress  in stress_list:

        os.system('curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=' + stress + f'+plant+microbial+tolerance&retmax=1000&retmode=xml" > articles_{stress}.xml')

        exit_file = open(f'articles_{stress}.xml', 'r', encoding = 'utf-8')
        list_ids = exit_file.read().split('<IdList>')[-1].split('</IdList>')[0].split('\n')[1:-1]
        list_ids = [x.strip('</Id>') for x in list_ids]

        pmc_list.append([stress, list_ids])

        exit_file.close()


    os.system('rm articles_stress.xml')

    return pmc_list



def write_text(stress_list, number_abstracts_per_stress, destination_path):
    """Creates a file for each retrieved abstract

    :param stress_list: file with different types of abiotic stress in plants
    :param number_abstracts_per_stress: int that indicates the number of abstracts intended for each stress type
    :param destination_path: destination path
    :return: file for each retrieved abstract
    """

    pmc_list = get_pmc_ids_list(stress_list)

    for list_ids in pmc_list:

        number_requests = 0
        counter = 0

        while number_requests < number_abstracts_per_stress and counter < len(list_ids):

            os.system('curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=' + list_ids[counter] + '&retmode=xml" > abstract.xml')

            presence = subprocess.Popen("grep '<AbstractText>' 'abstract.xml'", shell = True)

            return_code = presence.wait()

            if return_code != 1:

                try:

                    exit_file = open('abstract.xml', 'r', encoding = 'utf-8')
                    abstract = exit_file.read().split('<AbstractText>', 1)[-1].split('</AbstractText>', 1)[0]

                    save_language = ''

                    try:

                        for language in Detector(abstract).languages:
                            save_language = str(language).split()[1]
                            break

                    except:

                        pass

                    if save_language == 'English':
                        output = open(destination_path + '/' + list_ids[counter], 'w', encoding = 'utf-8')
                        output.write(abstract)
                        output.close()

                        number_requests += 1

                    else:
                        print(list_ids[counter], 'was discarded:', save_language)

                    exit_file.close()

                except UnicodeDecodeError:

                    pass

                except FileNotFoundError:

                    pass

            counter += 1

    os.system('rm abstract.xml')

    return


#### DIVIDED BY SENTENCES ABSTRACTS ####

def divided_by_sentences(corpus_path, geniass_path, destination_path):  # needs to be run from directory bin/geniass/
    """Creates a file for each divided by sentences abstract

    :param corpus_path: edited corpus path
    :param geniass_path: GENIA Sentence Splitter path
    :param destination_path: destination path
    :return: file for each divided by sentences abstract
    """

    os.system('rm -rf ' + destination_path + '* || true')

    for (dir_path, dir_names, file_names) in os.walk(corpus_path):

        for filename in file_names:

            os.system('./' + geniass_path + ' ' + corpus_path + filename + ' ' + destination_path + filename)

    return




#### RUN ####

def main():
    """Creates a directory with a file for each retrieved abstract divided by sentences

    :return: directory with a file for each retrieved abstract divided by sentences
    """

    number_of_abstracts_per_stress = int(sys.argv[1])

    os.system('mkdir -p corpora/pubmed_corpus/ || true')
    write_text('data/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt',
               'data/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes.txt', number_of_abstracts_per_stress, 'corpora/pubmed_corpus/')
    os.system('mkdir -p corpora/edited_corpus/ || true')
    os.system('cp corpora/pubmed_corpus/* corpora/edited_corpus/')
    os.chdir('bin/geniass/')
    divided_by_sentences('../../corpora/edited_corpus/', 'geniass', '../../corpora/pubmed_corpus/')
    os.chdir('../..')
    os.system('rm -rf corpora/edited_corpus/')

    return


if __name__ == "__main__":
    main()
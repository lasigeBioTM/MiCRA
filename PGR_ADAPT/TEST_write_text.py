import os
import subprocess
from polyglot.detect import Detector

from TEST_get_pmc_ids_list import get_pmc_ids_list

def write_text(stress_list, number_abstracts_per_stress, destination_path):
    """Creates a file for each retrieved abstract

    :param stress_list: file with different types of abiotic stress in plants
    :param number_abstracts_per_stress: int that indicates the number of abstracts intended for each stress type
    :param destination_path: destination path
    :return: file for each retrieved abstract
    """

    pmc_list = get_pmc_ids_list(stress_list)

    for stress_type in pmc_list:
        for list_ids in stress_type[1]:

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


with open("data/stress.txt","r") as f:
    f = f.readlines()
    f = [x.replace("\n","") for x in f]
    write_text(f,150,"data/abstracts.xml")
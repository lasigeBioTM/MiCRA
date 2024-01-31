import os

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


    # os.system('rm articles_stress.xml')

    return pmc_list
        
    # print (pmc_list)

with open("data/stress.txt","r") as f:
    f = f.readlines()
    f = [x.replace("\n","") for x in f]
    get_pmc_ids_list(f)
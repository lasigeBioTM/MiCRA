import pandas as pd
import os
import time
from get_pmcids import parse_synonyms_file



##################################################
#      CREATE INFO DATASET (SYNONYMS HANDLED)    #
##################################################


def create_info_dataset(checked_dataset, unique_dataset_path, info_dataset_path):
    """Handles stress synonyms in checked relations dataset for easier profiling and
    relation identification between relevant entities

    :param checked_dataset (str): dataset file (.txt) with checked relations
    :param unique_dataset_path (str): destination path to unique entries dataset file (synonyms and duplicates handled)
    :param info_dataset_path (str): destination path to info dataset file (synonyms handled)
    :return: tuple containing (number of positive relations in dataset, number of negative relations in dataset)
    :side effect: creates .csv files with annotated sentences, tagged entities, and relation between    
    """
    

    # Get synonym mapping for stress types
    ST_synonyms_path = os.path.join('bin','MER','data','stress_synonyms.txt')
    stress_synonyms_mapping = parse_synonyms_file(ST_synonyms_path)
    stress_synonym_to_key = {synonym: key for key, synonyms in stress_synonyms_mapping.items() for synonym in synonyms}


    # Get synonym mapping for plants
    PL_synonyms_path = os.path.join('bin','MER','data','plants_synonyms.txt')
    plant_synonyms_mapping = parse_synonyms_file(PL_synonyms_path)
    plant_synonym_to_key = {synonym: key for key, synonyms in plant_synonyms_mapping.items() for synonym in synonyms}


    # Get synonym mapping for microorganisms
    PL_synonyms_path = os.path.join('bin','MER','data','microorganisms_synonyms.txt')
    microorganism_synonyms_mapping = parse_synonyms_file(PL_synonyms_path)
    microorganism_synonym_to_key = {synonym: key for key, synonyms in microorganism_synonyms_mapping.items() for synonym in synonyms}
    

    with open(checked_dataset, 'r', encoding='utf-8') as original_dataset:
        lines = original_dataset.readlines()

    with open(info_dataset_path, 'w', encoding='utf-8') as dataset_to_write:

        with open(unique_dataset_path, 'w', encoding='utf-8') as unique_dataset_entries:

            unique_entries = set()
            for line in lines:
                id = (line.split(' | '))[0]
                microorganism = ((line.split(' | '))[1])
                stress = (line.split(' | '))[2]
                plant = (line.split(' | ')[3])
                text = (line.split(' | ')[4])
                relation = line.split(' | ')[5].strip()
                        
                # Replace stress term with main term if it's a synonym --> ex: "high temperature" (stress) is replaced by "heat" (stress)
                print(f'ORIGINAL STRESS: {stress}')
                if stress.lower() in stress_synonym_to_key.keys():
                    stress = stress_synonym_to_key[stress.lower()].capitalize()                
                else:   # If term is a main term or if it doesn't exist in the synonyms dictionary, don't replace it
                    stress = stress.capitalize()
                print(f'FINAL STRESS: {stress}\n')
            

                # Replace plant term with main term if it's a synonym --> ex: "red algae" is replaced by "Rhodophyta"
                print(f'ORIGINAL PLANT: {plant}')
                if plant in plant_synonym_to_key.keys():
                    plant = plant_synonym_to_key[plant].capitalize()                
                else:   # If term is a main term or if it doesn't exist in the synonyms dictionary, don't replace it
                    plant = plant.capitalize()
                print(f'FINAL PLANT: {plant}')


                # Replace microorganism term with main term if it's a synonym --> ex: "slime nets" is replaced by "Labyrinthulomycetes"
                print(f'ORIGINAL MICROORGANISM: {microorganism}')
                if microorganism in microorganism_synonym_to_key.keys():
                    microorganism = microorganism_synonym_to_key[microorganism].capitalize()
                else:   # If term is a main term or if it doesn't exist in the synonyms dictionary, don't replace it
                    microorganism = microorganism.capitalize()
                print(f'FINAL MICROORGANISM: {microorganism}')


                new_entry = f'{id} | {microorganism} | {stress} | {plant} | {text} | {relation}'

                # Remove duplicate entries after stress synonyms have been handled
                dataset_to_write.write(f'{new_entry}\n')
                if new_entry not in unique_entries:
                    unique_entries.add(new_entry)
                    unique_dataset_entries.write(f'{new_entry}\n')
                else:
                    continue
    
    return stress_synonyms_mapping


#####################################
#          CREATE DATAFRAME         #
#####################################

def createDF(dataset_file, separator):
    """Creates Pandas DataFrame from dataset .txt file

    :param dataset_file (str): dataset file (.txt)
    :param separator (str): character that separates columns in original dataset file
    :return: Pandas DataFrame with 6 columns: article ID, microorganism, stress, plant, text, and relation
    
    """
    
    df = pd.read_csv(dataset_file, sep=separator, header=None)
    df.columns = ['PMCID', "MICROORGANISM", "STRESS", "PLANT", "TEXT", "RELATION"]

    return df



################################################
#       CREATE DATASET INFORMATION FILES       #
################################################

def get_dataset_info(dataframe, destination_path):
    """Creates a file with dataset features: amount of positive and negative relations and relative frequency of each;
    number of occurrences for each stress type; number of occurrences of each of the 20 most frequent microorganisms and plants
    
    :param dataframe (df): Pandas DataFrame with 6 columns: article ID, microorganism, stress, plant, text, and relation
    :param destination_path (str): path to dataset features file
    :return side effect: creates a file with dataset features
    """
    
    with open(destination_path, 'w', encoding='utf-8') as composition_file:

        # Relation information
        relation_count = dataframe.value_counts(["RELATION"])
        YES_count = int(dataframe["RELATION"].value_counts()[" YES"])
        NO_count = int(dataframe["RELATION"].value_counts()[" NO"])
        TOTAL_relation_count = int(dataframe["RELATION"].value_counts()[" YES"] + dataframe["RELATION"].value_counts()[" NO"])
        YES_frequency = YES_count/TOTAL_relation_count * 100
        NO_frequency = NO_count/TOTAL_relation_count * 100

        # Stress information
        stress_count = dataframe.value_counts(["STRESS"])
        SALT_count = int(dataframe["STRESS"].str.lower().value_counts()[" salt "])
        HEAT_count = int(dataframe["STRESS"].str.lower().value_counts()[" heat "])
        DROUGHT_count = int(dataframe["STRESS"].str.lower().value_counts()[" drought "])
        COLD_count = int(dataframe["STRESS"].str.lower().value_counts()[" cold "])
        TOTAL_stress_count = int(dataframe["STRESS"].str.lower().value_counts()[" salt "] + \
                                    dataframe["STRESS"].str.lower().value_counts()[" heat "] + \
                                    dataframe["STRESS"].str.lower().value_counts()[" drought "] + \
                                    dataframe["STRESS"].str.lower().value_counts()[" cold "])
        SALT_frequency = SALT_count/TOTAL_stress_count * 100
        HEAT_frequency = HEAT_count/TOTAL_stress_count * 100
        DROUGHT_frequency = DROUGHT_count/TOTAL_stress_count * 100
        COLD_frequency = COLD_count/TOTAL_stress_count * 100

        # Microorganism information
        microorganism_count = dataframe.value_counts(["MICROORGANISM"]).head(15)    # Displays 15 most frequent microorganisms

        # Plant information
        plant_count = dataframe.value_counts(["PLANT"]).head(15)                    # Displays 15 most frequent plants

        entry = f'{relation_count}\
        \n\nRELATION FREQUENCY \
        \nPositive (relation found): {YES_frequency:.1f}%\
        \nNegative (relation not found): {NO_frequency:.1f}%\n\n------------------------------------------\
        \
        \n\n{stress_count}\
        \n\nSTRESS FREQUENCY \
        \nSalt stress: {SALT_frequency:.1f}%\
        \nDrought stress: {DROUGHT_frequency:.1f}%\
        \nHeat stress: {HEAT_frequency:.1f}%\
        \nCold stress: {COLD_frequency:.1f}%\
        \
        \n\nTop 15 Microorganisms in Dataset and # of Occurrences in Dataset: \
        \n{microorganism_count}\n\n------------------------------------------\
        \n\nTop 15 Plants in Dataset and # of Occurrences in Dataset: \
        \n{plant_count}'
        composition_file.write(entry)



def get_combinations(dataframe, destination_path, stress_synonyms):
    """Creates a .txt file with most to least common combinations of microorganism, stress and plant in dataset,
    with respective references

    :param dataframe (df): Pandas DataFrame with 6 columns: article ID, microorganism, stress, plant, text, and relation
    :param destination_path (str): path to dataset combinations file
    :param stress_synonyms (dict): dictionary mapping stress synonyms (values) to their main terms (keys)
    :return side effect: .txt file with most common combinations of related microorganism, stress and plant in dataset,
    plus references
    """

    link_prefix = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC'

    # Extract only positive relations
    df = dataframe.loc[dataframe['RELATION'] == " YES"]

    print(f'OG STRESSES IN DATASET:\n{df.loc[:,"STRESS"]}')

    # Group positive relations by 'MICROORGANISM', 'STRESS', and 'PLANT', then aggregate 'TEXT' and 'ID' entries
    grouped = df.groupby(['MICROORGANISM', 'STRESS', 'PLANT']).agg(
        count = ('PMCID', 'size'),   # Count occurrences
        references = ('TEXT', lambda x: '\n'.join(f"{text} ({link_prefix}{id})" for id, text in zip(df.loc[x.index, 'PMCID'], x)))  # Concatenate 'TEXT' and 'ID'
        ).reset_index()

    # Sort occurrences in descending order (most common occurrences appear first in file)
    sorted = grouped.sort_values('count', ascending=False)

    # Get combinations file for each stress type
    for stress in stress_synonyms.keys():
        print(f'Get combinations for "{stress}"')
        get_combinations_by_stress(df, destination_path, stress)

    # Write combinations and respective occurrences in file (descending order)
    with open(destination_path, 'w', encoding='utf-8') as combinations_file:
        for index, row in sorted.iterrows():
            microorganism = (row['MICROORGANISM']).strip()
            stress = (row['STRESS']).strip()
            plant = (row['PLANT']).strip()
            count = row['count']
            references = row['references']
            entry = (f"{microorganism} + {stress} + {plant} --> {count} occurrences\nReferences:\n{references}\n\n-------------------------------------\n\n")
            combinations_file.write(entry)



def get_combinations_by_stress(df, destination_path, stress):
    """Called by get_combinations() function. Creates a .txt file per stress type with most to least common combinations
    of microorganisms and plants in dataset, with respective references

    :param df (df): Pandas DataFrame with only positive relations between microorganism, stress and plant
    :param destination_path (str): path to dataset combinations file
    :param stress (str): stress type
    :return side effect: creates a .txt file for each stress type with most common combinations of related microorganisms
    and plants in dataset, plus references
    """

    link_prefix = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC'

    print(f'Stress to extract: {stress.capitalize()}')
    # Extract only stress type relations
    df = df.loc[df['STRESS'] == f' {stress.capitalize()} ']
    print(f'Stress dataframe:\n{df}\n\n')

    # Group relations by 'MICROORGANISM', and 'PLANT', then aggregate 'TEXT' and 'ID' entries
    grouped = df.groupby(['MICROORGANISM', 'PLANT']).agg(
        count = ('PMCID', 'size'),   # Count occurrences
        references = ('TEXT', lambda x: '\n'.join(f"{text} ({link_prefix}{id})" for id, text in zip(df.loc[x.index, 'PMCID'], x)))  # Concatenate 'TEXT' and 'ID'
        ).reset_index()
    print(f'Grouped dataframe:\n{grouped}\n\n')

    # Sort occurrences in descending order (most common occurrences appear first in file)
    sorted = grouped.sort_values('count', ascending=False)

    # Adapt file name from original destination path
    destination_path = destination_path.replace("_ALL.txt", "")

    # Write combinations and respective occurrences for each stress type in file
    write_file_path = os.path.join(f'{destination_path}_{stress}.txt')
    with open(write_file_path, 'w', encoding='utf-8') as stress_file:
        stress_file.write(f"\n** MICROORGANISM + PLANT COMBINATIONS FOR {stress.upper()} STRESS **\n\n")
        for index, row in sorted.iterrows():
            microorganism = (row['MICROORGANISM']).strip()
            plant = (row['PLANT']).strip()
            count = row['count']
            references = row['references']
            entry = (f"{microorganism} + {plant} --> {count} occurrences\nReferences:\n{references}\n\n-------------------------------------\n\n")
            stress_file.write(entry)



#####################
#        RUN        #
#####################

def main():
    """Produces .txt files with information regarding dataset profile and relevant combinations of entities

    :return: creates directory for dataset information files and produces 1) a file containing dataset features,
        2) a file containing all combinations of related microorganism, stress and plant in descending order of occurrence
        in dataset (with references), and 3) a file for each stress type containing all combinations of related microorganisms
        and plants in descending order of occurrence in dataset (with references)
    """

    start_time = time.time() #----------------------------------------------------------------------------------------------- LOG: TIME

    os.system('mkdir -p info || true')  # dir for dataset information files
    checked_dataset_path = os.path.join('2M-PAST','Checked_DS.txt')             # 2M-PAST/Checked_DS.txt'
    unique_dataset_path = os.path.join('info','Unique_Entries.txt')             # info/Unique_Entries,txt
    info_dataset_path = os.path.join('info','Info_DS.txt')                      # info/Info_DS.txt'
    combinations_path = os.path.join('info','combinations_ALL.txt')             # info/combinations_ALL.txt'
    dataset_profile_path = os.path.join('info','dataset_profile.txt')           # info/dataset_profile.txt'

    stress_synonyms = create_info_dataset(checked_dataset_path, unique_dataset_path, info_dataset_path)
    print(f"Full dataset created at 'info/Info_DS.txt'")

    df = createDF(info_dataset_path, '|')
    get_dataset_info(df, dataset_profile_path)
    get_combinations(df, combinations_path, stress_synonyms)

    print(f"\nInfo document creation time:  {time.time() - start_time:.1f} seconds") #----------------------------- LOG: TIME
    return


if __name__ == "__main__":
    main()

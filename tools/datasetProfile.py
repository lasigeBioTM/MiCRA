import pandas as pd


#####################################
#          CREATE DATAFRAME         #
#####################################

def createDF(dataset_file, separator, id):
    """Creates Pandas DataFrame from dataset .txt file

    :param dataset_file (str): dataset file (.txt)
    :param separator (str): character that separates columns in original dataset file
    :param id (str): 'PMCID' or 'DOI' (ID type associated with each dataset entry)
    :return: Pandas DataFrame with 6 columns: article ID, microorganism, stress, plant, text, and relation
    
    """
    
    df = pd.read_csv(dataset_file, sep=separator, header=None)
    id = id.upper()
    df.columns = [id, "MICROORGANISM", "STRESS", "PLANT", "TEXT", "RELATION"]

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
    
    with open(destination_path, 'w') as composition_file:

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
        METAL_count = int(dataframe["STRESS"].str.lower().value_counts()[" heavy metals "])       
        TOTAL_stress_count = int(dataframe["STRESS"].str.lower().value_counts()[" salt "] + \
                                    dataframe["STRESS"].str.lower().value_counts()[" heat "] + \
                                    dataframe["STRESS"].str.lower().value_counts()[" drought "] + \
                                    dataframe["STRESS"].str.lower().value_counts()[" cold "] + \
                                    dataframe["STRESS"].str.lower().value_counts()[" heavy metals "])
        SALT_frequency = SALT_count/TOTAL_stress_count * 100
        HEAT_frequency = HEAT_count/TOTAL_stress_count * 100
        DROUGHT_frequency = DROUGHT_count/TOTAL_stress_count * 100
        COLD_frequency = COLD_count/TOTAL_stress_count * 100
        METAL_frequency = METAL_count/TOTAL_stress_count * 100

        # Microorganism information
        microorganism_count = dataframe.value_counts(["MICROORGANISM"]).head(20)    # Displays 20 most frequent microorganisms

        # Plant information
        plant_count = dataframe.value_counts(["PLANT"]).head(20)                    # Displays 20 most frequent plants

        entry = f'{relation_count}\
        \n\nRELATION FREQUENCY \
        \nPositive (relation found): {YES_frequency:.1f}%\
        \nNegative (relation not found): {NO_frequency:.1f}%\n\n------------------------------------------\
        \
        \n\n{stress_count}\
        \n\nSTRESS FREQUENCY \
        \nSalt stress: {SALT_frequency:.1f}%\
        \nDrought stress: {DROUGHT_frequency:.1f}%\
        \nCold stress: {COLD_frequency:.1f}%\
        \nHeat stress: {HEAT_frequency:.1f}%\
        \nHeavy metal stress: {METAL_frequency:.1f}%\n\n------------------------------------------\
        \
        \n\n20 Top Microorganisms in Dataset and # of Occurrences in Dataset: \
        \n{microorganism_count}\n\n------------------------------------------\
        \n\n20 Top Plants in Dataset and # of Occurrences in Dataset: \
        \n{plant_count}'
        composition_file.write(entry)



def get_combinations(reference_type, dataframe, destination_path):
    """Creates a .txt file with most to least common combinations of microorganism, stress and plant in dataset,
    with respective references

    :param reference_type (str): 'pmcid' or 'doi' (type of IDs used in dataset)
    :param dataframe (df): Pandas DataFrame with 6 columns: article ID, microorganism, stress, plant, text, and relation
    :param destination_path (str): path to dataset combinations file
    :return side effect: .txt file with most common combinations of microorganism, stress and plant in dataset,
    plus references
    """

    if reference_type.lower() == 'pmcid':
        link_prefix = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC'
    elif reference_type.lower() == 'doi':
        link_prefix = 'https://doi.org/'


    # Group positive relations by 'MICROORGANISM', 'STRESS', and 'PLANT', then aggregate 'TEXT' and 'ID' entries
    grouped = dataframe[dataframe.RELATION == " YES"].groupby(['MICROORGANISM', 'STRESS', 'PLANT']).agg(
        count = (reference_type.upper(), 'size'),   # Count occurrences
        references = ('TEXT', lambda x: '\n'.join(f"{text} ({link_prefix}{id.strip()})" for id, text in zip(dataframe.loc[x.index, reference_type.upper()], x)))  # Concatenate 'TEXT' and 'ID'
        ).reset_index()

    # Sort occurrences in descending order (most common occurrences appear first in file)
    sorted = grouped.sort_values('count', ascending=False)

    # Get combinations file for each stress type
    for stress in dataframe.get('STRESS'):
        get_combinations_by_stress('doi', dataframe, destination_path, stress.lower().strip())

    # Write combinations and respective occurrences in file (descending order)
    with open(destination_path, 'w') as combinations_file:
        for index, row in sorted.iterrows():
            microorganism = (row['MICROORGANISM']).strip()
            stress = (row['STRESS']).strip()
            plant = (row['PLANT']).strip()
            count = row['count']
            references = row['references']
            entry = (f"{microorganism} + {stress} + {plant} --> {count} occurrences\nReferences:\n{references}\n\n-------------------------------------\n\n")
            combinations_file.write(entry)



def get_combinations_by_stress(reference_type, dataframe, destination_path, stress):
    """Called by get_combinations() function. Creates a .txt file per stress type with most to least common combinations
    of microorganisms and plants in dataset, with respective references

    :param reference_type (str): 'pmcid' or 'doi' (type of IDs used in dataset)
    :param dataframe (df): Pandas DataFrame with 6 columns: article ID, microorganism, stress, plant, text, and relation
    :param destination_path (str): path to dataset combinations file
    :param stress (str): stress type
    :return side effect: creates a .txt file for each stress type with most common combinations of microorganisms
    and plants in dataset, plus references
    """

    # Handle stress terms with blank spaces for file naming
    if ' ' in stress:
        stress = stress.replace(' ', '_')

    # Link prefix changes with reference type
    if reference_type.lower() == 'pmcid':
        link_prefix = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC'
    elif reference_type.lower() == 'doi':
        link_prefix = 'https://doi.org/'


    # Group positive relations of given stress type by 'MICROORGANISM' and 'PLANT', then aggregate 'TEXT' and 'ID' entries
    grouped = dataframe.loc[(dataframe['RELATION'] == " YES") & (dataframe['STRESS'] == f" {stress} ")].groupby(['MICROORGANISM', 'PLANT']).agg(
        count = (reference_type.upper(), 'size'),   # Count occurrences
        references = ('TEXT', lambda x: '\n'.join(f"{text} ({link_prefix}{id.strip()})" for id, text in zip(dataframe.loc[x.index, reference_type.upper()], x)))  # Concatenate 'TEXT' and 'ID'
        ).reset_index()

    # Sort occurrences in descending order (most common occurrences appear first in file)
    sorted = grouped.sort_values('count', ascending=False)

    # Adapt file name from original destination path
    destination_path = destination_path.replace("ALL.txt", "")

    # Write combinations and respective occurrences for each stress type in file
    with open(f"{destination_path}_{stress}.txt", 'w') as stress_file:
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
    """

    :return: 
    """

    df = createDF('datasetTOTAL.txt', '|', 'DOI')
    get_dataset_info(df, './dataset/INFO_dataset.txt')
    get_combinations('doi', df, './dataset/INFO_combinations_ALL.txt')

    return


if __name__ == "__main__":
    main()

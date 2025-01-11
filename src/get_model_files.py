import os
import csv
import re
import random


#################################################
#        CREATE TRAIN AND TEST FILES - CSV      #
#################################################


def get_tsv_files(dataset_file, train_proportion):
    """Takes the checked dataset and produces a .csv file with only the relation info ('1' if it exists, '0' if it doesn't) and
    the sentence with the tagged entities --> for model training purposes!!

    :param dataset_file (str): original dataset file (.txt)
    :param train_proportion (int): proportion (between 0 and 1) of instances from dataset that will be used for
    training the model (remainder of the dataset will be used for testing)
    :return side effect: creates .csv files with article IDs, annotated sentences, tagged entities, and relation
    between them ('1' if relation exists, '0' if it doesn't) for model training and testing purposes
    """

    with open(dataset_file, 'r', encoding='utf-8') as file:
        rows = [line.strip().split('|') for line in file]

    # Process each row
    processed_rows = []
    for row in rows:
        id, microorganism, stress, plant, text, relation = [item.strip() for item in row]
        
        # Transform RELATION to label
        label = '1' if relation == 'YES' else '0'
        
        # Annotate entities in text
        text = re.sub(fr'\b{stress}\b', f"<e2>{stress}</e2>", text, flags=re.IGNORECASE)
        text = re.sub(fr'\b{plant}\b', f"<e3>{plant}</e3>", text, flags=re.IGNORECASE)

        if '+' in microorganism:    # In case the instance refers to a combination of microorganisms, annotate them separately
            combined_MOs = microorganism.split(' + ')
            ch = "a"
            for MO in combined_MOs:
                text = re.sub(fr'\b{MO}\b', f"<e1{ch}>{MO}</e1{ch}>", text, flags=re.IGNORECASE)
                ch = chr(ord(ch) + 1)

        else:
            text = re.sub(fr'\b{microorganism}\b', f"<e1>{microorganism}</e1>", text, flags=re.IGNORECASE)
        
        processed_rows.append([id, microorganism, stress, plant, text, label])

    # Shuffle the rows
    random.shuffle(processed_rows)

    # Split into train and test sets
    split_index = int(len(processed_rows) * train_proportion)
    train_rows = processed_rows[:split_index]
    test_rows = processed_rows[split_index:]

    # Write train file
    train_path = os.path.join('model_data','2mpast_train.tsv')
    with open(train_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t', lineterminator='\n')
        writer.writerow(['label', 'text', 'microorganism', 'stress', 'plant', 'id'])
        for row in train_rows:
            # Format (tab-separated): [LABEL]  [TEXT]  [MICROORGANISM]  [STRESS]  [PLANT]  [ID]
            writer.writerow([row[5].strip(), row[4].strip('"'), row[1].strip(), row[2].strip(), row[3].strip(), row[0].strip()])

    # Write test file
    test_path = os.path.join('model_data','2mpast_test.tsv')
    with open(test_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t', lineterminator='\n')
        writer.writerow(['text', 'microorganism', 'stress', 'plant', 'id', 'true label'])
        for row in test_rows:
            # Format (tab-separated): [TEXT]  [MICROORGANISM]  [STRESS]  [PLANT]  [ID]  [TRUE LABEL]
            writer.writerow([row[4].strip('"'), row[1].strip(), row[2].strip(), row[3].strip(), row[0].strip(), row[5].strip()])

    print(f"Processing complete. {len(train_rows)} rows in 2mpast_train.tsv, {len(test_rows)} rows in 2mpast_test.tsv")




#####################
#        RUN        #
#####################

def main():
    """Creates model training and testing files from checked dataset in .tsv format

    :return: one .csv file for training and one .csv file for testing per id with relations between
      entities described as "YES" or "NO" for model training, and "TEST" for testing 
    """
    
    original_dataset_file = os.path.join('dataset','SS_Dataset.txt')

    os.system('mkdir -p model_data/tsv || true')
    
    # Default proportion of dataset allocated to training: 0.7
    training_proportion = 0.7

    get_tsv_files(original_dataset_file, training_proportion)
    print(f"Train and test datasets created in model_data/ directory")

    return


if __name__ == "__main__":
    main()
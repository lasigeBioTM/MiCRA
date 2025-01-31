import os


################################################
#           TEST FIRST-TIME ANNOTATORS         #
################################################

def testing_annotator():
    """Called by the get_checked_dataset() function. Produces a small test for new annotators to get acquainted
    with the relation validation system and rules.

    """

    annotator = input("Are you a first-time annotator? (y/n) ")
    if annotator.lower() == "y":
        print("\n----------------\nWelcome! Let's test some relations so you can get the hang of it (only 3 examples, don't worry!)\n(Please refrain from using the \"stop\" command at this stage)\n----------------")

        # Example 1: Relation exists
        print("EXAMPLE 1")
        test1 = check_relation("For instance, Bacillus subtilis SM21 has been shown to enhance the drought tolerance of cucumber (Cucumis sativus L.) plants by increasing the activity of SOD and mitigating the expression of genes encoding the cytosolic APX in cucumber leaf tissues.", "Bacillus subtilis SM21", "drought", "cucumber")
        if test1 == "YES":
            print("Correct! From the sentence, it is possible to establish a RELATION between the entities.\n")
        else:
            print("Sorry, that's incorrect! Given the sentence, it is possible to affirm that THERE IS A RELATION between the entities.\n")
        
        input("Press Enter to continue...\n-------------------------------\n")  

        # Example 2: Relation doesn't exist
        print("EXAMPLE 2")
        test2 = check_relation("Plant-growth-promoting rhizobacteria such as Bacillus, Enterobacter, Moraxella, and Pseudomonas have been isolated and inoculated into drought-stressed wheat plants.", "Bacillus", "Drought", "Wheat")
        if test2 == "NO":
            print("Correct! Although all 3 entity types exist in this sentence, there is NO RELATION between them.\n")
        else:
            print("Sorry, that's incorrect! Although all 3 entity types exist in this sentence, there is NO RELATION between them.\n")

        input("Press Enter to continue...\n-------------------------------\n")

        # Example 3: Relation doesn't exist (symbiosis/co-inoculation)
        print("EXAMPLE 3")
        test3 = check_relation("This paper demonstrates that the combination of Azospirillum brasilense and Pantoea dispersa in sweet pepper plants is able to partly ameliorate the effects of saline stress on growth.", "Azospirillum brasilense", "saline stress", "sweet pepper")
        if test3 == "NO":
            print("Correct! This microorganism participates in an association (co-inoculation/symbiosis/etc), so it can't be individually linked to stress tolerance in this plant.\n")
        else:
            print("Sorry, that's incorrect! Although a relation is described in the sentence, it includes an association of microorganisms, not a single one!\n")

        input("Press Enter to continue...\n-------------------------------\n")




################################################
#         CHECK RELATIONS IN RAW DATASET       #
################################################


def check_relation(text, microorganism, stress, plant):
    """Called by the get_checked_dataset() function. Asks user if relation can be found between entities given the text
    alone, and registers the input for relation tagging in final checked dataset.

    :param text (str): input text with potential relation
    :param microorganism (str): entity microorganism
    :param stress (str): entity stress
    :param plant (str): entity plant
    :return str: relation tag ("YES" or "NO") or "STOP" command
    
    """

    print(f'\nTEXT: {text}\n')
    relation_check = input(f'Based on the text alone, can we affirm that {microorganism} confers/improves tolerance to {stress} in {plant}?\n(y/n/stop) --> ')

    if relation_check.lower() == "y":
        relation = "YES"
        print("\nRelation found in text!\n-------------------------------")
    elif relation_check.lower() == "n":
        relation = "NO"
        print("\nRelation not found in text!\n\n-------------------------------")
    elif relation_check.lower() == "stop":
        relation = "STOP"
        return relation
    else:
        print("\nPlease try again!\n")
        relation = check_relation(text, microorganism, stress, plant)

    
    return relation



###################################
#      CREATE CHECKED DATASET     #
###################################


def get_checked_dataset(original_dataset, dataset_to_check, checked_dataset):
    """Opens original dataset file to check relations and asks for user input to manually tag them in dataset entries, writing
    these entries in a new checked dataset file. If user inputs "stop" word, creates a file with the remaining, unchecked dataset
    entries to continue later on.

    :param original_dataset (str): original dataset file
    :param dataset_to_check (str): unchecked dataset entries file (to read and update if it exists, to create if it doesn't)
    :param checked_dataset (str): final checked dataset
    :return side effect: creates a checked relations dataset
    :return potential side effect: creates an unchecked relations dataset if process is stopped
    
    """

    # Check if unchecked relations dataset file exists
    try:
        with open(dataset_to_check, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    # If it doesn't, open original dataset file (will only happen in the first run)
    except FileNotFoundError:
        testing_annotator()        
        with open(original_dataset, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    print("----------------------------\nAlright! Let's get started.\n----------------------------\n\n")

    # Initialize the unchecked entries
    unchecked_entries = list(lines)  # Copy all entries initially to unchecked list

    # Open checked dataset file in append mode
    with open(checked_dataset, 'a', encoding='utf-8') as checked:
        for line in lines:
            # Parse the line into components
            try:
                id, microorganism, stress, plant, text, label = line.strip().split(' | ', 5)
            except ValueError:
                print(f"Skipping malformed line: {line.strip()}")
                continue

            # Manually check the relation between entities in text
            relation = check_relation(text, microorganism, stress, plant)
            
            if relation == "STOP":
                print("\n**** Unchecked dataset entries stored. Re-run script to continue where you left off.")
                break  # Exit loop on "STOP"
            
            # Construct the checked entry and write to the file
            entry = f"{id} | {microorganism} | {stress} | {plant} | {text} | {relation}\n"
            checked.write(entry)

            # Remove the current entry from unchecked entries
            unchecked_entries.remove(line)

    # Handle remaining unchecked entries
    if unchecked_entries:
        print(f"Remaining unchecked entries: {len(unchecked_entries)}")
        with open(dataset_to_check, 'w', encoding='utf-8') as to_check:
            to_check.writelines(unchecked_entries)

    else:
        # Count True and False positives in checked dataset
        TruePositives = 0
        FalsePositives = 0

        with open(checked_dataset, 'r', encoding='utf-8') as checked:
            checked_entries = checked.readlines()

        for entry in checked_entries:
            if entry.strip.split(' | ')[5] == 'YES':
                TruePositives +=1
            else:
                FalsePositives +=1

        logfile_path = os.path.join('logfiles','06_checked_relations')
        with open(logfile_path, 'w', encoding='utf-8') as logfile:
            logfile.write(f'-----------------------------------------\n \
                                DATASET CREATED        \n----------------------------------------- \
                        \nTRUE POSITIVES: {TruePositives}\nFALSE POSITIVES: {FalsePositives}')
            
        # Remove dataset entries to check file (all checked!)
        os.system(f'rm {dataset_to_check}')




#####################
#        RUN        #
#####################

def main():
    """Asks for user input to check relations in dataset, then produces a final dataset with only 4 types of stress
    (handles stress synonyms) for easier entity mapping, as well as statistical analysis of dataset

    :return: final dataset with only 4 types of stress (handles stress synonyms) for easier entity mapping,
    as well as statistical analysis of dataset
    """      

    original_dataset = os.path.join('dataset','SS_Dataset.txt') # 'dataset/SS_Dataset.txt'
    to_check = os.path.join('dataset','KeepChecking_DS.txt')    # 'dataset/KeepChecking_DS.txt'
    checked = os.path.join('dataset','Checked_DS.txt')          # 'dataset/Checked_DS.txt'


    get_checked_dataset(original_dataset, to_check, checked)


    return


if __name__ == "__main__":
    main()
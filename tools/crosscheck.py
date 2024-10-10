import re


#########################################################
#                  GET RELEVANT STATS                   #
#########################################################


with open('datasetTOTAL.txt', 'r') as dataset:
    lines = dataset.readlines()

D_microorganisms = set()
D_plants = set()

for line in lines:
    microorganism = line.split(' | ')[1].strip()
    plant = line.split(' | ')[3].strip()

    D_microorganisms.add(microorganism)     # Microorganisms found in dataset
    D_plants.add(plant)                     # Plants found in dataset


with open('./bin/MER/data/microorganisms.txt', 'r') as microorganisms_classes:
    names_MOs = set(line.strip().lower() for line in microorganisms_classes)    # Microorganisms found in extracted classes labels file

with open('./bin/MER/data/plants.txt', 'r') as plants_classes:
    names_PLs = set(line.strip().lower() for line in plants_classes)            # Plants found in extracted classes labels file



# Crosscheck microorganism entities between dataset and extracted classes
countMOs = 0
MOs_notfound = set()
MOs_combs = set()
for microorganism in D_microorganisms:
    if microorganism.lower() in names_MOs:
        countMOs +=1
    elif re.search(r"\+", microorganism):       # Check combinations in dataset (ex: Bacillus subtilis + Mesorhizobium ciceri)
        MOs_combs.add(microorganism)
    else:
        MOs_notfound.add(microorganism)

check_percentageMOs = (countMOs/len(D_microorganisms))*100


# Crosscheck plant entities between dataset and extracted classes
countPLs = 0
PLs_notfound = set()
PLs_combs = set()
for plant in D_plants:
    if plant.lower() in names_PLs:
        countPLs +=1
    elif re.search(r"\+", plant):       # Check combinations in dataset (uncommon in plants, but just in case)
        PLs_combs.add(plant)
    else:
        PLs_notfound.add(plant)

check_percentagePLs = (countPLs/len(D_plants))*100



#########################################################
#                  DISPLAYING RESULTS                   #
#########################################################

print('\nDATASET vs EXTRACTED CLASSES CROSSCHECK\n')
print(f'% of dataset plants in extracted classes: {check_percentagePLs:.1f}')
print(f'% of dataset microorganisms in extracted classes: {check_percentageMOs:.1f}')


print('\n----------------------------\n\nMicroorganisms not found:')
if MOs_notfound == set():
    print('None')
else:
    print('\n'.join(MOs_notfound))

print(f'\nMicroorganism combinations in dataset:')
if MOs_combs == set():
    print('None')
else:
    print('\n'.join(MOs_combs))

print(f'\nPlants not found:')
if PLs_notfound == set():
    print('None')
else:
    print('\n'.join(PLs_notfound))

print(f'\nPlants combinations in dataset:')
if PLs_combs == set():
    print('None')
else:
    print('\n'.join(PLs_combs))

print('\n----------------------------')
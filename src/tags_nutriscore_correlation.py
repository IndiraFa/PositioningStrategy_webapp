import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from pathlib import Path
import argparse

# id == nom_recette sur streamlit 
def get_value_from_string(string):
    # Use re.findall to extract numbers
    numbers = re.findall(r'\d+\.\d+|\d+', string)

    # Convert numbers from string to numeric
    numbers = [float(num) if '.' in num else int(num) for num in numbers]
    return numbers

def get_text_from_string(string):
    # Use re.findall to extract words from list strings in recipe dataset
    wordsprep = re.findall(r'[a-zA-Z0-9-]+', string)

    # and prepocessing
    # wordsprep = list(map(lambda x: [word.lower for word in x], words))
    return wordsprep

class tags:# mettre en majuscule Tags
    def __init__(self, data, tag_target):
        self.data = data
        self.tag_target = tag_target
        self.tags, self.ids = self.get_data_tags()
        self.tags = self.preprocessing_data_tags()
    
    def get_data_tags(self):
        """
        Fonction permet d'extraire les tags des recettes et les index associés dans le DataFrame
        Input : dataframe de recettes avec colonnes 'tags', dans la colonne 'tags' les tags sont séparés par des virgules
        Output : list de tags et list index associés
        # traduction-->
        """
        # Création d'une liste vide pour stocker les tags
        tagsall = []
        indexall = []
        # Parcourir les lignes du DataFrame
        tagsall = list(self.data['tags'].apply(get_text_from_string))
        indexall = list(self.data.index)
        return tagsall , indexall

    def preprocessing_data_tags(self):
        """
        Fonction permet de prétraiter les tags des recettes, en les mettant en minuscule 
        et enlever les tirets
        Input: data tags 
        Output: data tags prétraité
        """
        listtags = self.tags
        print(type(listtags))
        # Metter en miniscule les tags
        self.tags = list(map(lambda x: [tag.lower() for tag in x], listtags))
        print(self.tags)
        # Enlever les tirets
        self.tags = list(map(lambda x: [tag.replace('-', ' ') for tag in x], listtags))
        return self.tags
    
    def extract_tag(self, tag):
        """
        Fonction permet d'extraire les recettes ayant un tag cible
        Input : tags cibles et list des tags des recettes
        Output : list des index des recettes ayant les tags cibles
        """
        ids_target = []
        # check type of tags, if not string, raise Error 
        if isinstance(tag, str) == False:
            raise ValueError("tag_target must be a string")
        else:
            for tagcase, id in zip(self.tags, self.ids):
                if tag in tagcase: 
                    ids_target.append(id)
        
        if len(ids_target) == 0:
            print("No recipe have this tag")
            return 0
        else:
            return ids_target
    
    def get_recipes_from_tags(self):
        """ Use to extract recipes with many tags """
        ids_target = []
        if len(self.tag_target) > 1:
            for tag in self.tag_target:
                ids_target.append(self.extract_tag(tag))
            # Union or intersection of recipes with tags
            # list recipes have all tags target
            # recipes1 = np.intersect1d(ids_target)
            recipes1 = set(ids_target[0]).intersection(*ids_target[1:])
            # list test have one tag target
            # recipes2 = np.union1d(ids_target)
            return ids_target, recipes1
        else:
            ids_target = self.extract_tag(self.tag_target)
            return ids_target
        

def main(args):
    tags_reference = args.tags_reference
    path = Path('/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit_Big_Data/dataset/RAW_recipes.csv')
    data = pd.read_csv(path)
    # dftags = data.tags.apply(get_text_from_string)

    #get list off all tags in the dataset
    tagsget, _ = tags(data, tags_reference).get_data_tags()

    # get recipes with tags target
    tags_instance = tags(data, tags_reference)
    ids_recipes_target = tags_instance.get_recipes_from_tags()
    print('number of recipes with tags target:', len(ids_recipes_target))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tags_reference', '-t', type=str, required=True, help='tags reference separated by comma')
    args = parser.parse_args()
    main(args)
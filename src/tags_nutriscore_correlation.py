import re
import os
import pandas as pd
import numpy as np
import sys, os
import argparse
import logging
import scipy.stats as stats
from functools import reduce
import toml
import streamlit as st
from db.db_instance import db_instance
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
import logging

logger = logging.getLogger("tags_nutriscore_correlation")


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load_streamlit_db(table_name, query=None):
    """
    Apply the streamlit database connection to load table from database.

    Returns:
        DataFrame: The database table.
    """
    if query is None:
        query = f'SELECT * FROM "{table_name}";'
    
    data = db_instance.fetch_data(query)
    return data


class DatabaseTable:
    """Class for creating a database table with sql"""

    def __init__(self, table_name, query=None, data=None):
        """
        Initialize the CreateDatabaseTable class.

        Args:
        - table_name (str): The name of the table to create.
        - toml_path (str): The path to the toml file containing 
        the database configuration.
        - data (DataFrame): The input dataset to create a table from.
            
        """
        # self.toml_path = toml_path
        # self.postgresql_config = self.read_toml_file()
        self.query = query
        self.data = data
        self.table_name = table_name

    # def read_toml_file(self):
    #     """
    #     Read a toml file and return the configuration settings.

    #     Args:
    #         toml_path (str): The path to the toml file.

    #     Returns:
    #         dict: A dictionary containing the configuration settings.
    #     """
    #     self.postgresql_config = toml.load(self.toml_path)['connections']['postgresql']
    #     return self.postgresql_config
    
    # def create_table(self):


    def apply_streamlit_db(self):
        """
        Apply the streamlit database connection to load table from database.

        Returns:
            DataFrame: The database table.
        """
        return load_streamlit_db(self.table_name, self.query)
    
    

class Utils:
    """Utility class for various helper functions."""

    @staticmethod
    def get_value_from_string(string):
        """
        Extract numbers from a string.

        Args:
            string (str): The input string containing numbers.

        Returns:
            list: A list of numbers extracted from the string.
        """
        numbers = re.findall(r'\d+\.\d+|\d+', string)
        numbers = [float(num) if '.' in num else int(num) for num in numbers]
        return numbers
    
    @staticmethod
    def get_text_from_string(string):
        """
        Extract text from a string.

        Args:
            string (str): The input string containing text.

        Returns:
            list: A list of text extracted from the string.
        """
        # Use re.findall to extract words from list strings in recipe dataset
        wordsprep = re.findall(r'[a-zA-Z0-9-]+', string)
        return wordsprep


class PreprocessTags:
    """Class for preprocessing tags in the dataset."""

    def __init__(self, data):
        """
        Initialize the PreprocessTags class.

        Args:
            data (DataFrame): The input dataset containing tags.
        """
        self.data = data
        self.tags, self.idrecipes = self.get_rawdata_tags()
        self.tags = self.split_text_tag()

    def split_text_tag(self):
        """
        Preprocess recipe tags by putting them in lowercase and removing hyphens.

        Returns:
            list: Preprocessed tags.
        """
        # put text in lowercase
        self.tags = list(map(lambda x: [tag.lower() for tag in x], self.tags))
        # Remove hyphens
        self.tags = list(map(lambda x: [tag.replace('-', ' ') for tag in x], self.tags))
        return self.tags

    def get_rawdata_tags(self):
        """
        Extract raw tags and ids from the dataset.

        Returns:
            tuple: A tuple containing lists of tags and ids.
        """
        tags = self.data['tags'].apply(Utils.get_text_from_string).tolist()
        idrecipes = self.data['id'].tolist()
        return tags, idrecipes

    def formatter_tags_data(self):
        """
        Format the tags data for further processing.

        Returns:
            DataFrame: A DataFrame with formatted tags data.
        """
        df = pd.DataFrame({
            'idrecipes': self.idrecipes,
            'tags': self.tags
        })
        formatted_data = df.explode('tags').reset_index(drop=True)
        return formatted_data


class Tags:
    """Class for handling tags and extracting recipes based on tags."""

    def __init__(self, tagsdata, tag_target):
        """
        Initialize the Tags class.

        Args:
            tagsdata (DataFrame): The input dataset containing tags and recipe IDs.
            tag_target (str): The target tag(s) for extraction.
        """
        self.tags = tagsdata['tags']
        self.idrecipes = tagsdata['idrecipes']
        self.tagsdata = tagsdata
        self.tag_target = tag_target

    def extract_tag(self, tag):
        """
        Extract recipes with a single target tag.

        Args:
            tag (str): The target tag to extract recipes for.

        Returns:
            list: A list of recipe IDs that have the target tag.
        """
        t = self.tagsdata
        # ids_target = self.tags[self.tags == tag].index.tolist()
        if (t['tags'] == tag).any():
            ids_target = t.where(t['tags'] == tag).dropna()['idrecipes'].astype(int).to_list()
            ids_target = np.unique(ids_target)
        else:
            ids_target = []
        return ids_target

    def get_recipes_from_tags(self):
        """
        Extract recipes with multiple target tags.

        Returns:
            list: A list of recipe IDs that have all the target tags.
        """
        ids_target = []
        tag_target = self.tag_target.split(',')

        if isinstance(tag_target, list):
            if len(tag_target) == 1:
                logger.info(f"single tag target : tag = {tag_target[0]}")
                ids_target = self.extract_tag(tag_target[0])
                if ids_target.any():
                    return ids_target
                else:
                    logger.error("Any recipe have this tag")
                    raise AssertionError("Any recipe have this tag")
            else:
                for tag in tag_target:
                    tmp = self.extract_tag(tag)
                    ids_target.append(tmp)
                    logger.info(f"multiple tags target : tag = {tag}, len = {len(tmp)}")
                    # ids_target.append(self.extract_tag(tag))
                # Union or intersection of recipes with tags
                # list recipes have all tags target
                intersection = list(reduce(lambda x, y: set(x) & set(y), ids_target))
                logger.info(f"recipes with all multiple tags target : len = {len(intersection)}")
                return intersection
                # list test have one tag target
                # recipes2 = np.union1d(ids_target)

        elif isinstance(tag_target, str):
            logger.info(f"single tag target : tag = {tag_target}")
            ids_target = self.extract_tag(tag_target)
            if ids_target.any():
                return ids_target
            else:
                logger.error("Any recipe have this tag")
                raise AssertionError("Any recipe have this tag")
            


def main(arg):
    tags_reference = arg
    # create test directory to save test output
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    dir_test = os.path.join(PARENT_DIR, 'tests/tags')

    # edit the path to the secrets.toml file
    tom_path = os.path.join(CURRENT_DIR, '.streamlit', 'secrets.toml')

    # Before analyse tags, we need to load the dataset and extract tags from the dataset and save on new dataframe
    # load raw data
    logger.info(f"Loading data from the database ...")
    # path = os.path.join(PARENT_DIR, 'dataset/RAW_recipes.csv')
    # df_raw = pd.read_csv('/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit_Big_Data/dataset/RAW_recipes.csv')
    q1 = 'SELECT name, id, tags FROM "raw_recipes";'
    df_raw = DatabaseTable('raw_recipes', query=q1).apply_streamlit_db()
    logger.info(f"Raw data loaded successfully, there are {df_raw.shape[0]} rows")

    # load dataset no outlier
    # df_nooutlier = pd.read_csv('/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit_Big_Data/dataset/nutrition_table_nutriscore_no_outliers.csv')
    df_nooutlier = DatabaseTable('NS_noOutliers').apply_streamlit_db()
    logger.info(f"Data no outlier loaded successfully, there are {df_nooutlier.shape[0]} rows")

    # if not os.path.exists(dir_test):
    #     os.makedirs(dir_test)
    # else:
    #     os.chdir(dir_test)
    #     # create new exploded tags file if not exists
    #     new_tags_file = os.path.join(dir_test, 'explodetags.csv')
    #     if not os.path.exists(new_tags_file):
    #         new_data_tags = PreprocessTags(df_raw).formatter_tags_data()
    #         new_data_tags.to_csv(new_tags_file, index=False, header=True)
    #     else:
    # new_data_tags = pd.read_csv('/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit_Big_Data/dataset/explodetags.csv')
    new_data_tags = DatabaseTable('explodetags').apply_streamlit_db() # with raw recipes with outliers
    logger.info(f"Data tags loaded successfully, there are {new_data_tags.shape[0]} rows")

    logger.info(f"Get tags reference from user, there are {tags_reference}")
    # get recipes with tags target
    tags_instance = Tags(new_data_tags, tags_reference)
    ids_recipes_target = np.array(tags_instance.get_recipes_from_tags())
    logger.info('number of recipes with tags target:', len(ids_recipes_target))

    try:
        len(ids_recipes_target) > len(tags_reference.split(','))
        ids_recipes_target = pd.Series(ids_recipes_target.T) # convert to pandas series or to list of integer values

        # combine two tables to get recipes from tags target
        raw_recipes_nutrition = df_raw.iloc[np.where(df_nooutlier['id'].isin(df_raw['id']))]
        logger.info(f"Shape of all tags without outliers: {raw_recipes_nutrition.shape}")
        raw_recipes_nutrition['nutriscore'] = df_nooutlier['nutriscore']
        raw_recipes_nutrition['label'] = df_nooutlier['label']
        ids_common = ids_recipes_target[ids_recipes_target.isin(df_nooutlier['id'])]
        recipes_tags = raw_recipes_nutrition[raw_recipes_nutrition['id'].isin(ids_common)]

        # get highest score and top 3 scores
        top3scores = np.unique(recipes_tags['nutriscore'])[-3:]
        maxscore = np.unique(recipes_tags['nutriscore'])[-1]

        # get recipes with highest score and top 3 scores
        recipes_highestscore = recipes_tags[recipes_tags['nutriscore'] == maxscore]

        # Prepare dataset for analysis
        ids_recipes_target = ids_recipes_target.astype(int)
        dfsort = df_nooutlier[df_nooutlier['id'].isin(ids_recipes_target)]
        dfsortname = df_raw[df_raw['id'].isin(ids_recipes_target)][['name', 'id']]
        dfsortinner = pd.merge(dfsort, dfsortname, on='id', how='inner')

    except AssertionError:
        logger.error('Any recipes have these tags target')
        raise AssertionError('Any recipes have these tags target')
    return recipes_tags, dfsortinner, recipes_highestscore #, recipes_top3scores, 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--tags_reference',
        '-t',
        type=str,
        required=True,
        help='tags reference separated by comma')
    args = parser.parse_args()
    main(args.tags_reference)

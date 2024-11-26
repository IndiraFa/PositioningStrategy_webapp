import re
import os
from pathlib import Path
import pandas as pd
import numpy as np
import argparse
from functools import reduce
import scipy.stats as stats
import psycopg2
import toml
from streamlit_todb import fetch_data_from_db_v2


# logging
import logging
# Configer the logging module
logging.basicConfig(
    level=logging.INFO, 
    # format of the log messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    handlers=[
        logging.FileHandler("tags.log"),  # save the logs in a file
        logging.StreamHandler()  # show the logs in the console
    ]
)

# Create a logger object
logger = logging.getLogger("tags_nutriscore_correlation")
logger.info("tags processing")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class DatabaseTable:
    """Class for creating a database table with sql"""

    def __init__(self, table_name, toml_path, data=None):
        """
        Initialize the CreateDatabaseTable class.

        Args:
        - table_name (str): The name of the table to create.
        - toml_path (str): The path to the toml file containing 
        the database configuration.
        - data (DataFrame): The input dataset to create a table from.
            
        """
        self.toml_path = toml_path
        self.postgresql_config = self.read_toml_file()
        self.data = data
        self.table_name = table_name

    def read_toml_file(self):
        """
        Read a toml file and return the configuration settings.

        Args:
            toml_path (str): The path to the toml file.

        Returns:
            dict: A dictionary containing the configuration settings.
        """
        self.postgresql_config = toml.load(self.toml_path)['connections']['postgresql']
        return self.postgresql_config
    
    # def create_table(self):
    
    def request_table(self):
        """
        Request the database table.

        Returns:
            DataFrame: The database table.
        """
        try:
            dbhost = self.postgresql_config['host']
            dbdatabase = self.postgresql_config['database']
            dbusername = self.postgresql_config['username']
            dbpassword = self.postgresql_config['password']
            dbport = int(self.postgresql_config['port'])

            logger.info("Connecting to the database ...")

            conn = psycopg2.connect(
                host=dbhost,
                port=dbport,
                user=dbusername,
                password=dbpassword,
                dbname=dbdatabase
            )

            logger.info("Successfully connected to the database")

            query = f'SELECT * FROM "{self.table_name}";'
            logger.info(f"Request line: {query}")
            df = pd.read_sql(query, conn)

            logger.info("Successfully read the data from the database")

            conn.close()
            logger.info("Connection to the database closed")
            return df
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

    def apply_streamlit_db(self):
        """
        Apply the streamlit database connection.

        Returns:
            DataFrame: The database table.
        """
        query = f'SELECT * FROM "{self.table_name}";'
        data1 = fetch_data_from_db_v2(query)
        return data1

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
        ids_target = t.where(t['tags'] == tag).dropna()['idrecipes'].astype(int).to_list()
        ids_target = np.unique(ids_target)
        return ids_target

    def extract_tag_v2(self, tag):
        """
        Extract recipes with a single target tag using a different method.

        Args:
            tag (str): The target tag to extract recipes for.

        Returns:
            list: A list of recipe IDs that have the target tag.
        """
        ids_target = self.tags.apply(lambda x: tag in x).index.tolist()
        return [self.ids[i] for i in ids_target]

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
                print("1", tag_target[0])
                logger.info(f"single tag target : tag = {tag_target[0]}")
                ids_target = self.extract_tag(tag_target[0])
                return ids_target
            else:
                for tag in tag_target:
                    tmp = self.extract_tag(tag)
                    ids_target.append(tmp)
                    print(f'2 : tag = {tag} - {len(tmp)}')
                    logger.info(f"multiple tags target : tag = {tag}, len = {len(tmp)}")
                    # ids_target.append(self.extract_tag(tag))
                # Union or intersection of recipes with tags
                # list recipes have all tags target
                intersection = list(reduce(lambda x, y: set(x) & set(y), ids_target))
                print('len of recipes1d :', len(intersection))
                logger.info(f"recipes with all multiple tags target : len = {len(intersection)}")
                return intersection
                # list test have one tag target
                # recipes2 = np.union1d(ids_target)

        elif isinstance(tag_target, str):
            print("3")
            logger.info(f"single tag target : tag = {tag_target}")
            ids_target = self.extract_tag(tag_target)
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
    df_raw = DatabaseTable('raw_recipes', tom_path).apply_streamlit_db()
    print('raw', df_raw.shape)

    # load dataset no outlier
    # df_nooutlier = pd.read_csv('/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit_Big_Data/dataset/nutrition_table_nutriscore_no_outliers.csv')
    df_nooutlier = DatabaseTable('NS_noOutliers', tom_path).apply_streamlit_db()
    print('nooutlier', df_nooutlier.shape)

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
    new_data_tags = DatabaseTable(
        'explodetags', 
        tom_path
    ).apply_streamlit_db() # with raw recipes with outliers
    print('new_data_tags', new_data_tags.shape)

    logger.info(f"Get tags reference from user, there are {tags_reference}")
    # get recipes with tags target
    tags_instance = Tags(new_data_tags, tags_reference)
    ids_recipes_target = np.array(tags_instance.get_recipes_from_tags())
    print('number of recipes with tags target:', len(ids_recipes_target))
    # logger.info('number of recipes with tags target:', len(ids_recipes_target))

    try:
        len(ids_recipes_target) > len(tags_reference.split(','))
        # recipes_target = data.iloc[ids_recipes_target]
        # print(recipes_target)
        # recipes_target.to_csv(Path(dir_test,f'out_selected_tags1.csv'), index=False, header=True)
        ids_recipes_target.tofile(
            Path(
                dir_test,
                f'out_selected_tags1.csv'),
            sep=",")
        ids_recipes_target = pd.Series(ids_recipes_target.T) # convert to pandas series or to list of integer values

        # combine two tables to get recipes from tags target
        raw_recipes_nutrition = df_raw.iloc[np.where(df_nooutlier['id'].isin(df_raw['id']))]
        print('Shape of all tags without outliers:', raw_recipes_nutrition.shape)
        raw_recipes_nutrition['nutriscore'] = df_nooutlier['nutriscore']
        raw_recipes_nutrition['label'] = df_nooutlier['label']
        ids_common = ids_recipes_target[ids_recipes_target.isin(df_nooutlier['id'])]
        print(ids_common)
        # recipes_tags = raw_recipes_nutrition.iloc[ids_common]
        recipes_tags = raw_recipes_nutrition[raw_recipes_nutrition['id'].isin(ids_common)]
        print('result:', recipes_tags.head())

        # recipes_tags_withoutlier = df_raw.iloc[np.where(ids_recipes_target.id.isin(df_raw.id))]


        # get highest score and top 3 scores
        top3scores = np.unique(recipes_tags['nutriscore'])[-3:]
        maxscore = np.unique(recipes_tags['nutriscore'])[-1]

        # get recipes with highest score and top 3 scores
        recipes_highestscore = recipes_tags[recipes_tags['nutriscore'] == maxscore]
        # print('highest score:', recipes_highestscore)

        # Prepare dataset for analysis
        ids_recipes_target = ids_recipes_target.astype(int)
        dfsort = df_nooutlier[df_nooutlier['id'].isin(ids_recipes_target)]
        dfsortname = df_raw[df_raw['id'].isin(ids_recipes_target)][['name', 'id']]
        dfsortinner = pd.merge(dfsort, dfsortname, on='id', how='inner')

    except AssertionError:
        logger.error('Any recipes have these tags target')
        # print('Any recipes have these tags target together')
        # for i in range(len(tags_reference.split(','))):
        #     ids_recipes_target[i].tofile(
        #         Path(
        #             dir_test,
        #             f'out_selected_tags{i + 1}.csv'),
        #         sep=",")
            # recipes_target = data.iloc[ids_recipes_target[i]]
            # print(recipes_target)
            # recipes_target.to_csv(Path(dir_test,f'out_selected_tags{i+1}.csv'), index=False, header=True)

        
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

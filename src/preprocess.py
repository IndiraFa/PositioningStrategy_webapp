import sys
import os
import pandas as pd
import re
import logging
import toml
from sqlalchemy import create_engine

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = logging.getLogger("preprocess")

#Define the configuration for the data preprocessing
configs = {
    'nutritioncolname': 
    ['calories', 'total_fat_%', 'sugar_%',
        'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
    'grillecolname': 
    ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%',
        'dv_sodium_%', 'dv_protein_%'],
    'dv_calories': 2000
}


class Datatools:
    @staticmethod
    def get_value_from_string(string):
        try:
            # Extract numbers from the string using regular expressions
            numbers = re.findall(r"\d+\.\d+|\d+", string)
            # Convert the extracted numbers to floats
            return [float(num) for num in numbers]
        except Exception as e:
            logger.error(f"Error while extracting numbers from string: {e}")
            return []


class Preprocessing:
    def __init__(self, data, configs):
        try:
            # Use the provided DataFrame directly
            self.rawdata = data
        except Exception as e:
            logger.error(f"Error while loading data: {e}")
        self.configs = configs
        # Initialize dictionaries to store mu and sigma values
        self.mu_values = {}
        self.sigma_values = {}
        # Perform initial data processing steps
        self.formatdata = self.get_formatted_nutrition()
        self.normaldata = self.set_dv_normalisation()
        self.prefiltredata = self.prefiltrage()
        self.gaussiandata, self.outliers = self.gaussian_normalisation()
        self.denormalizedata, self.denormalized_outliers = \
        self.Denormalisation(self.gaussiandata, self.outliers)

    def get_raw_nutrition(self):
        try:
            # Extract 'id' and 'nutrition' columns from raw data
            return self.rawdata[['id', 'nutrition']]
        except KeyError:
            logger.error("Columns 'id' and 'nutrition' not found in the dataset")
            return pd.DataFrame()

    def get_formatted_nutrition(self):
        try:
            # Format the nutrition data by extracting numerical values
            data = self.get_raw_nutrition()
            formatted_data = (
                data['nutrition']
                .apply(lambda x: Datatools.get_value_from_string(x))
            )
            # Create a df with the formatted data and add the 'id' column
            table = pd.DataFrame(
                formatted_data.tolist(),
                columns=self.configs['nutritioncolname']
            )
            table['id'] = data['id'].values
            return table
        except KeyError as e:
            logger.error(f"Error while formatting nutrition data: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return pd.DataFrame()

    def set_dv_normalisation(self):
        try:
            # Normalize the nutrition data based on daily values (DV)
            dv_calories = self.configs['dv_calories']
            fttable = self.formatdata
            table = pd.DataFrame()
            table['id'] = fttable['id']
            # Calculate the percentage of daily values for each nutrient
            table['dv_calories_%'] = (
                fttable['calories'] * 100 / dv_calories
                ).round(2)
            for col in self.configs['nutritioncolname'][1:]:
                table[f'dv_{col}'] = (
                    (fttable[col] * dv_calories / fttable['calories'])
                    .round(2)
                )
            self.normaldata = table
            return table
        except KeyError as e:
            logger.error(f"Error during data normalization: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return pd.DataFrame()

    def prefiltrage(self):
        try:
            # Copy the normalized data for pre-filtering
            table_prefiltre = self.normaldata.copy()

            # Define thresholds for each column
            thresholds = {
                'dv_calories_%': 5000,
                'dv_total_fat_%': 5000,
                'dv_sugar_%': 50000,
                'dv_sodium_%': 5000,
                'dv_protein_%': 2000,
                'dv_sat_fat_%': 2000,
                'dv_carbs_%': 5000
            }

            # Identify and combine outliers for each column based on 
            # predefined thresholds
            outliers = pd.concat([table_prefiltre[table_prefiltre[col] > \
            threshold] for col, threshold in thresholds.items()])\
                .drop_duplicates()

            # Filter out the visible outliers from different columns
            for col, threshold in thresholds.items():
                table_prefiltre = table_prefiltre[table_prefiltre[col]\
                                                   <= threshold]

            # Store the outliers
            self.outliers = outliers

            return table_prefiltre
    
        except KeyError as e:
            logger.error(f"Error during data pre-filtering: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return pd.DataFrame()

    def gaussian_normalisation(self):
        gauss_configs = {'colname': [
            'dv_calories_%',
            'dv_total_fat_%',
            'dv_sugar_%',
            'dv_sodium_%',
            'dv_protein_%',
            'dv_sat_fat_%',
            'dv_carbs_%'
        ]}
        try:
            table_gauss = self.prefiltredata.copy()
            
            # Apply Gaussian normalization to each column
            for col in gauss_configs['colname']:
                mu = table_gauss[col].mean()
                sigma = table_gauss[col].std()
                table_gauss[col] = (table_gauss[col] - mu) / sigma

                # Store the mu and sigma values
                self.mu_values[col] = mu
                self.sigma_values[col] = sigma

            table_gauss = table_gauss.dropna()

            # Copy the DataFrame for further processing
            DF_noOutliers = table_gauss.copy()
            DF_outliers = self.outliers.copy()


            # Identify and remove outliers (values >= 3) for each column
            for col in DF_noOutliers.columns:
                if col == 'id':
                    continue
                col_outliers = DF_noOutliers[DF_noOutliers[col] >= 3]

                DF_outliers = pd.concat([DF_outliers, col_outliers])
                DF_noOutliers = DF_noOutliers[DF_noOutliers[col] < 3].copy()

            # Store the new outliers
            self.outliers = DF_outliers.drop_duplicates()

            return DF_noOutliers, DF_outliers
        except KeyError as e:
            logger.error(f"Error during Gaussian normalization: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return pd.DataFrame()

    # denormalisation of the data from the gaussian_normalisation     
    def Denormalisation(self, DF_noOutliers, DF_outliers): 
        try:
            # Denormalize the Gaussian normalized data
            finalDF_noOutliers = DF_noOutliers.copy()
            finalDF_outliers = DF_outliers.copy()
            
            # Combine the columns from grillecolname with 
            # dv_total_fat_% and dv_carbs_%
            columns_to_denormalize = (
                self.configs['grillecolname'] + ['dv_total_fat_%',
                                                  'dv_carbs_%']
            )
            
            for col in columns_to_denormalize:
                mu = self.mu_values[col]
                sigma = self.sigma_values[col]
                finalDF_noOutliers[col] = finalDF_noOutliers[col] * sigma + mu
                finalDF_outliers[col] = finalDF_outliers[col] * sigma + mu

            return finalDF_noOutliers, finalDF_outliers
        except KeyError as e:
            logger.error(f"Error during data denormalization: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return pd.DataFrame()
        
    def SQL_database(self):
        # Lire les informations de connexion depuis secrets.toml
        secrets = toml.load('secrets.toml')
        postgresql_config = secrets['connections']['postgresql']
        # Create a PostgreSQL database and store the preprocessed data
        try:
            # Informations de connexion à la base de données PostgreSQL
            db_host = postgresql_config['host']
            db_name = postgresql_config['database']
            db_user = postgresql_config['username']
            db_password = postgresql_config['password']
            db_port = postgresql_config['port'] 

            # Créer une connexion à la base de données PostgreSQL
            engine = create_engine(
                f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/'
                f'{db_name}'
            )
            conn = engine.connect()

            # Store the formatted data in the database
            self.formatdata.to_sql(
                'Formatted_data', conn, if_exists='replace',index=False
            )
            # Store normalized data in the database
            self.normaldata.to_sql(
                'nutrition_withOutliers', conn, if_exists='replace',
                  index=False
            )
            # Store finalDF_noOutliers from Denormalisation(self, 
            # DF_noOutliers, DF_outliers) in the database
            self.denormalizedata.to_sql(
                'nutrition_noOutliers', conn, if_exists='replace',
                  index=False
            )
            # Store finalDF_outliers from Denormalisation(self,
            #  DF_noOutliers, DF_outliers) in the database
            self.denormalized_outliers.to_sql(
                'outliers', conn, if_exists='replace', index=False
            )
            # Store the gaussian normalized data in the database
            self.gaussiandata.to_sql(
                'gaussian_norm_data', conn, if_exists='replace', index=False
            )
            # Store the prefiltered data in the database
            self.prefiltredata.to_sql(
                'prefiltre_data', conn, if_exists='replace', index=False
            )

            # Close the database connection
            conn.close()
        except Exception as e:
            logger.error(f"Error while creating PostgreSQL database: {e}")


def main():
    # Lire les informations de connexion depuis secrets.toml
    secrets = toml.load('secrets.toml')
    postgresql_config = secrets['connections']['postgresql']
    # Informations de connexion à la base de données PostgreSQL
    db_host = postgresql_config['host']
    db_name = postgresql_config['database']
    db_user = postgresql_config['username']
    db_password = postgresql_config['password']
    db_port = postgresql_config['port']

    # Créer une connexion à la base de données PostgreSQL
    engine = create_engine(
        f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    )
    conn = engine.connect()
    
    # Read raw_recipes data from the database
    query = "SELECT * FROM raw_recipes"
    df = pd.read_sql_query(query, conn)
    
    # Close the database connection
    conn.close()

    # Create an instance of the Preprocessing class
    preprocessing_instance = Preprocessing(df, configs)

    # Save the preprocessed data to the database
    preprocessing_instance.SQL_database()

    # Get the formatted and normalized nutrition tables
    nutrition_table = preprocessing_instance.formatdata
    nutrition_table_normal = preprocessing_instance.normaldata

    logger.debug(nutrition_table.head())
    logger.debug(nutrition_table_normal.head())
    return nutrition_table, nutrition_table_normal


if __name__ == '__main__':
    main() 

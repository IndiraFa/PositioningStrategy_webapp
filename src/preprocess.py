import pandas as pd
import numpy as np
import re
from pathlib import Path
from tabulate import tabulate


class Datatools:
    @staticmethod # method independent of the instance state
    def get_value_from_string(string):
        try : 
            # use of re.findall to extract numbers (floats and integers)
            numbers = re.findall(r"\d+\.\d+|\d+", string)
            # Convert the extracted numbers to float or int
            numbers = [float(num) for num in numbers]
            return numbers
        except Exception as e:
            print(f"Error while extracting numbers from string : {e}")
            return []
        
class Preprocessing:
    def __init__(self, path, configs):
        try:
            # Load raw data from the specified CSV file
            self.rawdata = pd.read_csv(path, sep = ',')
        except FileNotFoundError:
            # Print an error message if the file is not found
            print(f"File {path} not found")
        self.configs = configs
        self.formatdata = self.get_formatted_nutrition()
        self.normaldata = self.set_dv_normalisation()
        self.prefiltredata = self.prefiltrage()
        self.gaussiandata = self.gaussian_normalisation()
    
    def get_raw_nutrition(self):
        try:
            # Extraction of id and nutrition columns only
            return self.rawdata[['id','nutrition']]
        except KeyError:
            # Print an error message if the columns are not found
            print("Columns 'id' and 'nutrition' not found in the dataset")
            return pd.DataFrame()
    
    def get_formatted_nutrition(self):
        try:
            # Creation of new columns for nutritional data
            data = self.get_raw_nutrition()
            formatted_data = data['nutrition'].apply(lambda x: Datatools.get_value_from_string(x))
            # Create a DataFrame with the formatted data and add the 'id' column
            table = pd.DataFrame(formatted_data.tolist(), columns=self.configs['nutritioncolname'])
            table['id'] = data['id'].values
            return table
        except KeyError as e:
            # Print an error message if formatting fails
            print(f"Error while formatting nutrition data : {e}")
        except Exception as e:
            # Print an unexpected error message
            print(f"Unexpected error : {e}")
            return pd.DataFrame()
    
    def set_dv_normalisation(self):
        try:
            # Creation of a dv_calories_% column to normalize nutritional values
            # Against the recommended daily intake
            dv_calories = self.configs['dv_calories']
            fttable = self.formatdata
            table = pd.DataFrame()
            table['id'] = fttable['id']
            # Calculate the percentage of daily values for each nutrient
            table['dv_calories_%'] = (fttable['calories'] * 100 / dv_calories).round(2)
            for col in self.configs['nutritioncolname'][1:]:
                table[f'dv_{col}'] = (fttable[col] * dv_calories /fttable['calories']).round(2)
            return table
        except KeyError as e:
            print(f"Erreur lors de la normalisation des données : {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            return pd.DataFrame()
    

    def prefiltrage(self):
        try:
            # Pre-filter the data to remove extreme outliers
            initial_count = len(self.normaldata)
            print(f"Number of rows before pre-filtering: {initial_count}")

            table_prefiltre = self.normaldata.copy()

            # Identify outliers for each column based on predefined thresholds
            outliers_calories = table_prefiltre[table_prefiltre['dv_calories_%'] > 5000]
            outliers_total_fat = table_prefiltre[table_prefiltre['dv_total_fat_%'] > 5000]
            outliers_sugar = table_prefiltre[table_prefiltre['dv_sugar_%'] > 50000]
            outliers_sodium = table_prefiltre[table_prefiltre['dv_sodium_%'] > 5000]
            outliers_protein = table_prefiltre[table_prefiltre['dv_protein_%'] > 2000]
            outliers_sat_fat = table_prefiltre[table_prefiltre['dv_sat_fat_%'] > 2000]
            outliers_carbs = table_prefiltre[table_prefiltre['dv_carbs_%'] > 5000]

            # Combine all outliers into a single DataFrame
            outliers = pd.concat([outliers_calories, outliers_total_fat, outliers_sugar, outliers_sodium, outliers_protein, outliers_sat_fat, outliers_carbs]).drop_duplicates()

            # Filter out the visible outliers from different columns
            table_prefiltre = table_prefiltre[table_prefiltre['dv_calories_%'] <= 5000]
            table_prefiltre = table_prefiltre[table_prefiltre['dv_total_fat_%'] <= 5000]
            table_prefiltre = table_prefiltre[table_prefiltre['dv_sugar_%'] <= 50000]
            table_prefiltre = table_prefiltre[table_prefiltre['dv_sodium_%'] <= 5000]
            table_prefiltre = table_prefiltre[table_prefiltre['dv_protein_%'] <= 2000]
            table_prefiltre = table_prefiltre[table_prefiltre['dv_sat_fat_%'] <= 2000]
            table_prefiltre = table_prefiltre[table_prefiltre['dv_carbs_%'] <= 5000]

            final_count = len(table_prefiltre)
            print(f"Number of rows after pre-filtering: {final_count}")
            print(f"Number of outliers removed during pre-filtering: {initial_count - final_count}")
            print("\n")

            # Store the outliers
            self.outliers = outliers

            return table_prefiltre
        except KeyError as e:
            # Print an error message if pre-filtering fails
            print(f"Error during data pre-filtering: {e}")
            return pd.DataFrame()
        except Exception as e:
            # Print an unexpected error message
            print(f"Unexpected error: {e}")
            return pd.DataFrame()

    def gaussian_normalisation(self):
        gauss_configs = {'colname': ['dv_calories_%', 'dv_total_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%', 'dv_sat_fat_%', 'dv_carbs_%']}
        try:
            table_gauss = self.prefiltredata.copy()
            
            initial_outliers_count = len(self.outliers)
            print(f"Number of rows in the outliers DataFrame before processing: {initial_outliers_count}")

            # Apply Gaussian normalization to each column
            for col in gauss_configs['colname']:
                table_gauss[col] = (table_gauss[col] - table_gauss[col].mean()) / table_gauss[col].std()

            table_gauss = table_gauss.dropna()

            # Copy the DataFrame for further processing
            finalTable_noOutliers = table_gauss.copy()
            Total_outliers = self.outliers.copy()

            print(f"Size of finalTable_noOutliers before processing: {len(finalTable_noOutliers)}")
            print(f"Size of Total_outliers before processing: {len(Total_outliers)}")
            print("\n")

            # Identify and remove outliers (values >= 3) for each column
            for col in finalTable_noOutliers.columns:
                if col == 'id':
                    continue
                col_outliers = finalTable_noOutliers[finalTable_noOutliers[col] >= 3]
                print(f"Number of outliers found in column {col}: {len(col_outliers)}")
                Total_outliers = pd.concat([Total_outliers, col_outliers])
                finalTable_noOutliers = finalTable_noOutliers[finalTable_noOutliers[col] < 3].copy()

            # Store the new outliers
            self.outliers = Total_outliers.drop_duplicates()

            print("\n")
            print(f"Size of finalTable_noOutliers after processing: {len(finalTable_noOutliers)}")
            print(f"Size of Total_outliers after processing: {len(Total_outliers)}")
            print("\n")

            return finalTable_noOutliers
        except KeyError as e:
            # Print an error message if Gaussian normalization fails
            print(f"Error during Gaussian normalization: {e}")
            return pd.DataFrame()
        except Exception as e:
            # Print an unexpected error message
            print(f"Unexpected error: {e}")
            return pd.DataFrame()


def main():
    path = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/data_base/RAW_recipes.csv'
    configs = {
    'nutritioncolname':['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
    'grillecolname':['dv_calories_%', 'dv_sat_fat_%', "dv_sugar_%", 'dv_sodium_%', 'dv_protein_%'],
    'dv_calories' : 2000
    }

    nutrition_table = Preprocessing(path, configs).formatdata
    nutrition_table_normal = Preprocessing(path, configs).normaldata
    print(nutrition_table.head())
    print(nutrition_table_normal.head())
    return nutrition_table, nutrition_table_normal

if __name__ == '__main__':
    main()


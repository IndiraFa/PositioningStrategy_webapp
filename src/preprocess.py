import pandas as pd
import numpy as np
import re
from pathlib import Path

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
            self.rawdata = pd.read_csv(path, sep = ',')
        except FileNotFoundError:
            print(f"File {path} not found")
        self.configs = configs
        self.formatdata = self.get_formatted_nutrition()
        self.normaldata = self.set_dv_normalisation()
    
    def get_raw_nutrition(self):
        try:
            # extraction of id and nutrition columns only
            return self.rawdata[['id','nutrition']]
        except KeyError:
            print("Columns 'id' and 'nutrition' not found in the dataset")
            return pd.DataFrame()
    
    def get_formatted_nutrition(self):
        try:
            # creation of new columns for nutritional data
            data = self.get_raw_nutrition()
            formatted_data = data['nutrition'].apply(lambda x: Datatools.get_value_from_string(x))
            table = pd.DataFrame(formatted_data.tolist(), columns=self.configs['nutritioncolname'])
            table['id'] = data['id'].values
            return table
        except KeyError as e:
            print(f"Error while formatting nutrition data : {e}")
        except Exception as e:
            print(f"Unexpected error : {e}")
            return pd.DataFrame()
    
    def set_dv_normalisation(self):
        try:
            # creation of a dv_calories_% column to normalize nutritional values
            # against the recommended daily intake
            dv_calories = self.configs['dv_calories']
            fttable = self.formatdata
            table = pd.DataFrame()
            table['id'] = fttable['id']
            table['dv_calories_%'] = fttable['calories'] * 100 / dv_calories
            for col in self.configs['nutritioncolname'][1:]:
                table[f'dv_{col}'] = fttable[col] * dv_calories /fttable['calories']
            return table
        except KeyError as e:
            print(f"Erreur lors de la normalisation des données : {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Erreur inattendue : {e}")
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


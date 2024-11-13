import pandas as pd
import re
# from tabulate import tabulate

configs = {
        'nutritioncolname': [
            'calories',
            'total_fat_%',
            'sugar_%',
            'sodium_%',
            'protein_%',
            'sat_fat_%',
            'carbs_%'
        ],
        'grillecolname': [
            'dv_calories_%',
            'dv_sat_fat_%',
            'dv_sugar_%',
            'dv_sodium_%',
            'dv_protein_%'
        ],
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
            # Print an error message if extraction fails
            print(f"Error while extracting numbers from string: {e}")
            return []


class Preprocessing:
    def __init__(self, path, configs):
        try:
            # Load raw data from the specified CSV file
            self.rawdata = pd.read_csv(path, sep=',')
        except FileNotFoundError:
            # Print an error message if the file is not found
            print(f"File {path} not found")
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
            # Print an error message if the columns are not found
            print("Columns 'id' and 'nutrition' not found in the dataset")
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
            # Print an error message if formatting fails
            print(f"Error while formatting nutrition data: {e}")
            return pd.DataFrame()
        except Exception as e:
            # Print an unexpected error message
            print(f"Unexpected error: {e}")
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
            # Print an error message if normalization fails
            print(f"Error during data normalization: {e}")
            return pd.DataFrame()
        except Exception as e:
            # Print an unexpected error message
            print(f"Unexpected error: {e}")
            return pd.DataFrame()

    def prefiltrage(self):
        try:
            # Pre-filter the data to remove extreme outliers
            initial_count = len(self.normaldata)
            print(f"Number of rows before pre-filtering: {initial_count}")

            table_prefiltre = self.normaldata.copy()

            # Identify outliers for each column based on predefined thresholds
            outliers_calories = table_prefiltre[
                table_prefiltre['dv_calories_%'] > 5000
            ]
            outliers_total_fat = table_prefiltre[
                table_prefiltre['dv_total_fat_%'] > 5000
            ]
            outliers_sugar = table_prefiltre[
                table_prefiltre['dv_sugar_%'] > 50000
            ]
            outliers_sodium = table_prefiltre[
                table_prefiltre['dv_sodium_%'] > 5000
            ]
            outliers_protein = table_prefiltre[
                table_prefiltre['dv_protein_%'] > 2000
            ]
            outliers_sat_fat = table_prefiltre[
                table_prefiltre['dv_sat_fat_%'] > 2000
            ]
            outliers_carbs = table_prefiltre[
                table_prefiltre['dv_carbs_%'] > 5000
            ]

            # Combine all outliers into a single DataFrame
            outliers = pd.concat([
                outliers_calories,
                outliers_total_fat,
                outliers_sugar,
                outliers_sodium,
                outliers_protein, 
                outliers_sat_fat,
                outliers_carbs
            ]).drop_duplicates()

            # Filter out the visible outliers from different columns
            table_prefiltre = table_prefiltre[
                table_prefiltre['dv_calories_%'] <= 5000
            ]
            table_prefiltre = table_prefiltre[
                table_prefiltre['dv_total_fat_%'] <= 5000
            ]
            table_prefiltre = table_prefiltre[
                table_prefiltre['dv_sugar_%'] <= 50000
            ]
            table_prefiltre = table_prefiltre[
                table_prefiltre['dv_sodium_%'] <= 5000
            ]
            table_prefiltre = table_prefiltre[
                table_prefiltre['dv_protein_%'] <= 2000
            ]
            table_prefiltre = table_prefiltre[
                table_prefiltre['dv_sat_fat_%'] <= 2000
            ]
            table_prefiltre = table_prefiltre[
                table_prefiltre['dv_carbs_%'] <= 5000
            ]

            final_count = len(table_prefiltre)
            print(f"Number of rows after pre-filtering: {final_count}")
            print(
                f"Number of outliers removed during pre-filtering: "
                f"{initial_count - final_count}"
            )
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
            
            initial_outliers_count = len(self.outliers)
            print(f"Number of rows in the outliers DataFrame before processing: "
                  f"{initial_outliers_count}")  # test unitaire

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

            print(
                f"Size of DF_noOutliers before processing: "
                f"{len(DF_noOutliers)}")  # test unitaire
            print(
                f"Size of Total_outliers before processing: "
                f"{len(DF_outliers)}")  # test unitaire
            print("\n")

            # Identify and remove outliers (values >= 3) for each column
            for col in DF_noOutliers.columns:
                if col == 'id':
                    continue
                col_outliers = DF_noOutliers[DF_noOutliers[col] >= 3]
                print(
                    f"Number of outliers found in column {col}: "
                    f"{len(col_outliers)}")
                DF_outliers = pd.concat([DF_outliers, col_outliers])
                DF_noOutliers = DF_noOutliers[DF_noOutliers[col] < 3].copy()

            # Store the new outliers
            self.outliers = DF_outliers.drop_duplicates()

            print("\n")
            print(
                f"Size of DF_noOutliers after processing: "
                f"{len(DF_noOutliers)}")  # test unitaire
            print(f"Size of DF_outliers after processing: {len(DF_outliers)}")
            print("\n")

            return DF_noOutliers, DF_outliers
        except KeyError as e:
            # Print an error message if Gaussian normalization fails
            print(f"Error during Gaussian normalization: {e}")
            return pd.DataFrame()
        except Exception as e:
            # Print an unexpected error message
            print(f"Unexpected error: {e}")
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
                self.configs['grillecolname'] + ['dv_total_fat_%', 'dv_carbs_%']
            )
            
            for col in columns_to_denormalize:
                mu = self.mu_values[col]
                sigma = self.sigma_values[col]
                finalDF_noOutliers[col] = finalDF_noOutliers[col] * sigma + mu
                finalDF_outliers[col] = finalDF_outliers[col] * sigma + mu

            return finalDF_noOutliers, finalDF_outliers
        except KeyError as e:
            # Print an error message if denormalization fails
            print(f"Error during data denormalization: {e}")
            return pd.DataFrame()
        except Exception as e:
            # Print an unexpected error message
            print(f"Unexpected error: {e}")
            return pd.DataFrame()


def main():
    path = './datasets/RAW_recipes.csv'

    # Create an instance of the Preprocessing class
    preprocessing_instance = Preprocessing(path, configs)
    # Get the formatted and normalized nutrition tables
    nutrition_table = preprocessing_instance.formatdata
    nutrition_table_normal = preprocessing_instance.normaldata
    # Print the first few rows of each table
    print(nutrition_table.head())
    print(nutrition_table_normal.head())
    return nutrition_table, nutrition_table_normal


if __name__ == '__main__':
    main()

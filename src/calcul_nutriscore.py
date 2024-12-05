import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
from sqlalchemy import create_engine
import toml
import logging

logger = logging.getLogger("app.calcul_nutriscore")


class NutriScore:
    """
    This Class calculates the NutriScore for each recipe in the dataset.

    Parameters
    ----------
    data : pd.DataFrame
        The dataset containing the nutritional information for each recipe.
    grille : pd.DataFrame
        The nutritional table containing the thresholds for each nutrient.
    configs : dict
        A dictionary containing the configuration parameters for the
        NutriScore calculation.

    Methods
    -------
    calcul_nutriscore()
        Calculate the NutriScore for each row in the dataset.
    set_scorelabel()
        Assign NutriScore labels (A-E) based on the calculated scores.
    stock_database()
        Store the NutriScore data in a PostgreSQL database
    """
    def __init__(self, data, grille, configs):
        """
        Method to initialize the NutriScore instance.

        Parameters
        ----------
        data : pd.DataFrame
            The dataset containing the nutritional information for each recipe.

        grille : pd.DataFrame
            The nutritional table containing the thresholds for each nutrient.

        configs : dict
            A dictionary containing the configuration parameters for the
            NutriScore calculation.
        """
        self.data = data
        self.grille = grille
        self.configs = configs

        # Calculate NutriScore and assign labels
        self.nutriscore = self.calcul_nutriscore()
        self.nutriscore_label = self.set_scorelabel()

    def calcul_nutriscore(self):
        """
        Calculate the NutriScore for each row in the dataset.

        Parameters
        ----------
        None

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the calculated NutriScore for each recipe.

        Raises
        ------
        ValueError
            If the column "nutriscore" is missing from the dataframe.        
        """
        data = self.data.copy()
        data['nutriscore'] = 14.0  # Start with a base score of 14

        grillecolname = self.configs['grillecolname']

        for nutrient in grillecolname:
            if nutrient in self.grille.columns:
                nutrient_grille = self.grille
                nutrient_values = data[nutrient].values

                for i, grille_row in nutrient_grille.iterrows():
                    prev_value = -np.inf if i == 0 else \
                                 nutrient_grille[nutrient].iloc[i - 1]
                    if np.isnan(grille_row[nutrient]):
                        # Handle the last range where the upper limit is 
                        # undefined
                        mask = (-nutrient_values > prev_value) if \
                            nutrient == "dv_protein_%" else \
                                (nutrient_values > prev_value)
                        data.loc[mask, 'nutriscore'] -= grille_row['points']
                        break
                    # Apply the NutriScore logic for valid ranges
                    mask = (-nutrient_values > prev_value) & \
                        (-nutrient_values <= grille_row[nutrient]) if \
                            nutrient == "dv_protein_%" else \
                           (nutrient_values > prev_value) & \
                            (nutrient_values <= grille_row[nutrient])
                    data.loc[mask, 'nutriscore'] -= grille_row['points']

        return data
    
    def set_scorelabel(self):
        """
        Assigns NutriScore labels (A-E) based on the calculated scores.

        Parameters
        ----------
        None

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the NutriScore labels for each recipe.

        Raises
        ------
        ValueError
            If the column "nutriscore" is missing from the dataframe.        
        """
        score = self.nutriscore
        if 'nutriscore' not in score.columns:
            raise ValueError(
                'The column "nutriscore" is missing from the dataframe.'
            )

        # Assign labels based on score thresholds
        score['label'] = ''
        score.loc[score['nutriscore'] >= 12, 'label'] = 'A'
        score.loc[
            (score['nutriscore'] >= 9) & (score['nutriscore'] < 12),
            'label'
        ] = 'B'
        score.loc[
            (score['nutriscore'] >= 6) & (score['nutriscore'] < 9),
            'label'
        ] = 'C'
        score.loc[
            (score['nutriscore'] >= 3) & (score['nutriscore'] < 6),
            'label'
        ] = 'D'
        score.loc[score['nutriscore'] < 3, 'label'] = 'E'
        
        return score

    def stock_database(self):
        """
        Stores the NutriScore data in a PostgreSQL database.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        Exception
            If an error occurs while storing the data in the database.        
        """
        secrets = toml.load('secrets.toml')
        postgresql_config = secrets['connections']['postgresql']
        try:
            # Establish a database connection
            engine = create_engine(f'postgresql://{postgresql_config["username"]}:{postgresql_config["password"]}'
                                   f'@{postgresql_config["host"]}:{postgresql_config["port"]}/{postgresql_config["database"]}')
            with engine.connect() as conn:
                # Save the NutriScore data to the database
                self.nutriscore_label.to_sql(
                    'NS_withOutliers',
                    conn,
                    if_exists='replace',
                    index=False
                )
                logging.info(
                    "NutriScore data successfully stored in the database."
                )
        except Exception as e:
            logging.error(f"Error storing data in the database: {e}")


class Plot:
    """
    This class generates and saves distribution plots for the NutriScore data.

    Parameters
    ----------
    data : pd.Series
        The data to be plotted.
    title : str
        The title of the plot.
    xlabel : str
        The label for the x-axis.
    ylabel : str
        The label for the y-axis.
    output_path : str
        The path to save the plot.

    Methods
    -------
    plot_distribution()
        Plot and save a histogram of the data.
    plot_distribution_label(labels)
        Plot and save a count plot for the NutriScore labels
    """
    def __init__(
            self,
            data,
            title=None,
            xlabel=None,
            ylabel=None,
            output_path=None
        ):
        """
        Method to initialize the Plot instance.

        Parameters
        ----------
        data : pd.Series
            The data to be plotted.
        title : str
            The title of the plot.
        xlabel : str
            The label for the x-axis.
        ylabel : str
            The label for the y-axis.
        output_path : str
            The path to save the plot.
        """
        self.data = data
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.output_path = output_path

    def plot_distribution(self):
        """
        Plot and save a histogram of the data.

        Parameters
        ----------
        None
        
        Returns
        -------
        None
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(self.data, bins=20, edgecolor='k', alpha=0.7)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        plt.savefig(self.output_path)
        plt.show()

    def plot_distribution_label(self, labels):
        """
        Plot and save a count plot for the NutriScore labels.
        
        Parameters
        ----------
        labels : list
            List of labels to be plotted.  

        Returns
        -------
        None
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(x=self.data, order=labels)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        plt.savefig(self.output_path)
        plt.show()


def main():
    """
    Main function to orchestrate data processing, NutriScore calculation, 
    and visualization.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Load database credentials from a TOML file
    secrets = toml.load('secrets.toml')
    postgresql_config = secrets['connections']['postgresql']
    try:
        # Connect to the PostgreSQL database
        engine = create_engine(
            f'postgresql://{postgresql_config["username"]}:{postgresql_config["password"]}'
                               f'@{postgresql_config["host"]}:{postgresql_config["port"]}/{postgresql_config["database"]}')
        with engine.connect() as conn:
            # Load data from the database
            df = pd.read_sql_query("SELECT * FROM raw_recipes", conn)
            df_grille = pd.read_sql_query("SELECT * FROM nutrient_table", conn)
            df_normalized_data = pd.read_sql_query(
                'SELECT * FROM "nutrition_withOutliers"',
                conn
            )

        # Configuration for the NutriScore calculation
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

        # Calculate NutriScore and store results in the database
        nutri_score_instance = NutriScore(
            df_normalized_data,
            df_grille,
            configs
        )
        nutri_score_instance.stock_database()

        #Generate and save distribution plots
        Plot(
            nutri_score_instance.nutriscore['nutriscore'],
            title='NutriScore Distribution',
            xlabel='NutriScore',
            ylabel='Number of Recipes',
            output_path='nutriscore_distribution.png'
        ).plot_distribution()
        Plot(
            nutri_score_instance.nutriscore_label['label'],
            title='NutriScore Label Distribution',
            xlabel='Labels',
            ylabel='Number of Recipes',
            output_path='nutriscore_label_distribution.png'
        ).plot_distribution_label(labels=['A', 'B', 'C', 'D', 'E'])
    except Exception as e:
        logging.error(f"Error in the main program: {e}")


if __name__ == "__main__":
    main()

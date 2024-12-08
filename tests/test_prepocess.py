import unittest
import pandas as pd
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from preprocess import Preprocessing, Datatools, configs

class TestPreprocessing(unittest.TestCase):

    def setUp(self):
        """Configuration initiale avant chaque test."""
        # Exemple de données d'entrée
        self.sample_data = pd.DataFrame({
            'id': [1, 2, 3],
            'nutrition': [
                '200 kcal, 10g fat, 5g sugar, 400mg sodium, 3g protein, 2g sat fat, 30g carbs',
                '300 kcal, 15g fat, 10g sugar, 500mg sodium, 5g protein, 3g sat fat, 40g carbs',
                '400 kcal, 20g fat, 8g sugar, 600mg sodium, 6g protein, 4g sat fat, 50g carbs'
            ]
        })
        self.preprocessor = Preprocessing(self.sample_data, configs)

    def test_get_value_from_string(self):
        """Test de la méthode statique pour extraire les valeurs numériques."""
        input_string = '200 kcal, 10g fat, 5g sugar'
        expected_output = [200.0, 10.0, 5.0]
        self.assertEqual(Datatools.get_value_from_string(input_string), expected_output)

    def test_get_raw_nutrition(self):
        """Test de la méthode get_raw_nutrition."""
        result = self.preprocessor.get_raw_nutrition()
        self.assertEqual(list(result.columns), ['id', 'nutrition'])
        self.assertEqual(len(result), 3)

    def test_get_formatted_nutrition(self):
        """Test de la méthode get_formatted_nutrition."""
        result = self.preprocessor.get_formatted_nutrition()
        self.assertEqual(list(result.columns), configs['nutritioncolname'] + ['id'])
        self.assertEqual(len(result), 3)

    def test_set_dv_normalisation(self):
        """Test de la méthode set_dv_normalisation."""
        result = self.preprocessor.set_dv_normalisation()
        self.assertTrue('dv_calories_%' in result.columns)
        self.assertEqual(len(result), 3)

    def test_prefiltrage(self):
        """Test de la méthode prefiltrage."""
        result = self.preprocessor.prefiltrage()
        self.assertTrue(len(result) <= len(self.preprocessor.normaldata))

    def test_gaussian_normalisation(self):
        """Test de la méthode gaussian_normalisation."""
        gauss_data, outliers = self.preprocessor.gaussian_normalisation()
        self.assertTrue('dv_calories_%' in gauss_data.columns)
        self.assertTrue(len(gauss_data) + len(outliers) != len(self.preprocessor.prefiltredata))

    
    def test_denormalisation(self):
        """Test de la méthode denormalisation avec des données simulées."""
        # Données simulées pour tester Denormalisation
        gauss_data = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [0.5, 0.8, 0.3]
        })
        outliers = pd.DataFrame({
            'id': [4],
            'value': [1.5]
        })

        # Étape 2 : Appliquer la dénormalisation
        result, result2 = self.preprocessor.Denormalisation(gauss_data, outliers)

        # Vérification si les DataFrames résultants sont vides (normalement oui car on a des données simulées)
        assert  result.empty, "Le DataFrame result ne doit pas contenir de données"
        assert  result2.empty, "Le DataFrame result2 ne doit pas contenir de données"



    


if __name__ == '__main__':
    unittest.main()
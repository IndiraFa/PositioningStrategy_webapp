import unittest
import pandas as pd
import sys, os
from unittest.mock import patch
import logging
import toml
from unittest.mock import MagicMock


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),\
                                              '..', 'src')))

from preprocess import Preprocessing, Datatools, configs, main

logger = logging.getLogger("test_preprocess")

class TestPreprocessing(unittest.TestCase):

    def setUp(self):
        """Initial configuration for the tests."""
        logger.debug("Exemple de données d'entrée")
        self.sample_data = pd.DataFrame({
            'id': [1, 2, 3],
            'nutrition': [
                '200 kcal, 10g fat, 5g sugar, 400mg sodium,\
                      3g protein, 2g sat fat, 30g carbs',
                '300 kcal, 15g fat, 10g sugar, 500mg sodium,\
                      5g protein, 3g sat fat, 40g carbs',
                '400 kcal, 20g fat, 8g sugar, 600mg sodium,\
                      6g protein, 4g sat fat, 50g carbs'
            ]
        })
        self.preprocessor = Preprocessing(self.sample_data, configs)
    
    @patch("preprocess.logger.error")
    def test_init_logs_exception(self, mock_logger):
        logger.debug("Invalid data to test the __init__ method")
        invalid_data = object()  
        configs = {"param1": "value1"}
        
        try:
            Preprocessing(invalid_data, configs)
        except Exception as e:
            logger.debug("Verify that the logger was called to log the error")
            pass  

        logger.debug("Verify that the logger was called to log the error")

        logger.debug("Verify that the logger was called to log the error")
        mock_logger.assert_called()

        logger.debug("Take arguments passed to the logger.error method")
        args, _ = mock_logger.call_args

        logger.debug("Verify that the error message is correct")
        self.assertEqual(args[0],\
                          "Error during data denormalization: 'grillecolname'")


    def test_get_value_from_string(self):
        """Static method test for get_value_from_string."""
        input_string = '200 kcal, 10g fat, 5g sugar'
        expected_output = [200.0, 10.0, 5.0]
        self.assertEqual(Datatools.get_value_from_string(input_string),\
                          expected_output)

        logger.debug("Case with invalid values in the input string")
        problematic_inputs = [None, "", {}, 123, 45.67, ["abc"]]
        
        for input_value in problematic_inputs:
            result = Datatools.get_value_from_string(input_value)
            assert result == [], f"Expected empty list for input \
                {input_value}, got {result}"


    def test_get_raw_nutrition(self):
        """Test of the get_raw_nutrition method."""
        result = self.preprocessor.get_raw_nutrition()
        self.assertEqual(list(result.columns), ['id', 'nutrition'])
        self.assertEqual(len(result), 3)

    def test_get_raw_nutrition_invalid(self):
        """Test get_raw_nutrition with invalid input."""
        logger.debug("Test problematic inputs for get_raw_nutrition.")
        problematic_inputs = [None, "", {}, 123, 45.67, ["abc"]]

        for input_value in problematic_inputs:
            with self.assertRaises(Exception):
                preprocessor = Preprocessing(input_value, self.configs)
                preprocessor.get_raw_nutrition()
        logger.debug("Invalid input test passed for get_raw_nutrition.")
    

    def test_get_formatted_nutrition(self):
        """Test of the get_formatted_nutrition method."""
        result = self.preprocessor.get_formatted_nutrition()
        self.assertEqual(list(result.columns), \
                         configs['nutritioncolname'] + ['id'])
        self.assertEqual(len(result), 3)

    def test_set_dv_normalisation(self):
        """Test of the set_dv_normalisation method."""
        result = self.preprocessor.set_dv_normalisation()
        self.assertTrue('dv_calories_%' in result.columns)
        self.assertEqual(len(result), 3)

    def test_prefiltrage(self):
        """Test of the prefiltrage method."""
        result = self.preprocessor.prefiltrage()
        self.assertTrue(len(result) <= len(self.preprocessor.normaldata))

    def test_gaussian_normalisation(self):
        """Test of the gaussian_normalisation method."""
        gauss_data, outliers = self.preprocessor.gaussian_normalisation()
        self.assertTrue('dv_calories_%' in gauss_data.columns)
        self.assertTrue(len(gauss_data) + len(outliers) != \
                        len(self.preprocessor.prefiltredata))

    
    def test_denormalisation(self):
        """Test of the Denormalisation method."""
        logger.debug("Simulate data for the Denormalisation method")
        gauss_data = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [0.5, 0.8, 0.3]
        })
        outliers = pd.DataFrame({
            'id': [4],
            'value': [1.5]
        })

        result, result2 = \
            self.preprocessor.Denormalisation(gauss_data, outliers)

        logger.debug("Verify the output of the Denormalisation method")
        assert  result.empty, "DataFrame result must be empty"
        assert  result2.empty, "DataFrame result2 must be empty"



    @patch('preprocess.logger')  
    def test_get_formatted_nutrition_keyerror(self, mock_logger):
        logger.debug("Create test data with missing columns")
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'nutrition': ['abc', 'def', 'ghi']  
        })
        preprocessor = Preprocessing(data, configs)

        preprocessor.get_formatted_nutrition()

        logger.debug("Verfy that logger.error was called for the error")
        mock_logger.error.assert_called()


    @patch('preprocess.logger') 
    def test_gaussian_normalisation_keyerror(self, mock_logger):
        logger.debug("Create test data with missing columns")
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'calories': [200, 300, 400],
        })
        preprocessor = Preprocessing(data, configs)

        logger.debug("Set the prefiltered With missing columns")
        preprocessor.prefiltredata = pd.DataFrame({'id': [1, 2, 3]})  

        logger.debug("Call the gaussian_normalisation method")
        result, outliers = preprocessor.gaussian_normalisation() 

        logger.debug("Verify that logger.error was called for the error")
        mock_logger.error.assert_called()



    @patch('preprocess.create_engine') 
    @patch('preprocess.toml.load')  
    def test_SQL_database(self, mock_toml_load, mock_create_engine):
        """Test SQL_database with mocked database interaction."""
        
        logger.debug("Simulate the content of the secrets.toml file")
        mock_toml_load.return_value = {
            'connections': {
                'postgresql': {
                    'host': 'localhost',
                    'database': 'test_db',
                    'username': 'test_user',
                    'password': 'test_password',
                    'port': '5432'
                }
            }
        }
        
        logger.debug("Simulate the database connection and \
                     the result of the SQL query")
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_conn
        
        logger.debug("Simulate the DataFrame returned by the SQL query")
        preprocessor = Preprocessing(None, {})
        preprocessor.formatdata = MagicMock()
        preprocessor.normaldata = MagicMock()
        preprocessor.denormalizedata = MagicMock()
        preprocessor.denormalized_outliers = MagicMock()
        preprocessor.gaussiandata = MagicMock()
        preprocessor.prefiltredata = MagicMock()
        
        logger.debug("Call the SQL_database method")
        preprocessor.SQL_database()
        
        logger.debug("Verify that the methods have been called")

        preprocessor.formatdata.to_sql.assert_called_once_with(
            'Formatted_data', mock_conn, if_exists='replace', index=False
        )
        preprocessor.normaldata.to_sql.assert_called_once_with(
            'nutrition_withOutliers', mock_conn, if_exists='replace', index=False
        )
        preprocessor.denormalizedata.to_sql.assert_called_once_with(
            'nutrition_noOutliers', mock_conn, if_exists='replace', index=False
        )
        preprocessor.denormalized_outliers.to_sql.assert_called_once_with(
            'outliers', mock_conn, if_exists='replace', index=False
        )
        preprocessor.gaussiandata.to_sql.assert_called_once_with(
            'gaussian_norm_data', mock_conn, if_exists='replace', index=False
        )
        preprocessor.prefiltredata.to_sql.assert_called_once_with(
            'prefiltre_data', mock_conn, if_exists='replace', index=False
        )

        logger.debug("Verify that the connection has been closed")
        mock_conn.close.assert_called_once()

        logger.debug("Verify that the engine has been disposed")
        mock_create_engine.assert_called_once_with(
            'postgresql://test_user:test_password@localhost:5432/test_db'
        )


class TestMainFunction(unittest.TestCase):

    logger.debug("Test the main function")

    @patch('preprocess.toml.load')  
    @patch('preprocess.create_engine')  
    @patch('preprocess.pd.read_sql_query')  
    @patch('preprocess.Preprocessing')  
    def test_main(self, mock_preprocessing, mock_read_sql_query, mock_create_engine, mock_toml_load):
        logger.debug("Verify the main function with mocked database \
                     interaction")
        mock_toml_load.return_value = {
            'connections': {
                'postgresql': {
                    'host': 'localhost',
                    'database': 'test_db',
                    'username': 'user',
                    'password': 'password',
                    'port': 5432
                }
            }
        }

        logger.debug("Simulate the database connection and the result \
                     of the SQL query")
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_conn = MagicMock()
        mock_engine.connect.return_value = mock_conn

        logger.debug("Simulate the DataFrame returned by the SQL query")
        mock_read_sql_query.return_value = pd.DataFrame({
            'id': [1, 2],
            'recipe_name': ['Recipe 1', 'Recipe 2'],
            'ingredient': ['Ingredient 1', 'Ingredient 2']
        })

        logger.debug("Simulate the Preprocessing instance")
        mock_instance = MagicMock()
        mock_preprocessing.return_value = mock_instance
        mock_instance.formatdata = \
            pd.DataFrame({'id': [1, 2],'calories': [100, 200]})
        mock_instance.normaldata = \
            pd.DataFrame({'id': [1, 2], 'calories_normalized': [0.1, 0.2]})
        mock_instance.SQL_database.return_value = None

        logger.debug("Call the main function")
        nutrition_table, nutrition_table_normal = main()

        logger.debug("Verify that the methods have been called")
        mock_toml_load.assert_called_once_with('secrets.toml')  
        mock_create_engine.assert_called_once() 
        mock_read_sql_query\
            .assert_called_once_with("SELECT * FROM raw_recipes", mock_conn) 
        mock_instance.SQL_database.assert_called_once() 
        self.assertEqual(nutrition_table.shape, (2, 2))  
        self.assertEqual(nutrition_table_normal.shape, (2, 2)) 


if __name__ == '__main__':
    unittest.main()

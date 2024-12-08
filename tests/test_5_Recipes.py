import sys,os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'src')
    ))
import tags_nutriscore_correlation
import importlib.util


spec = importlib.util.spec_from_file_location(
    "module_5_Recipes",
    os.path.join(os.path.dirname(__file__), 
                 '../src/pages/5_Recipes.py')
)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class TestRecipesApp(unittest.TestCase):

    @patch('streamlit.dataframe')
    def test_display_datatable(self, mock_st):
        """
        Test display_datatable function.

        Args:
            mock_st (MagicMock): st.dataframe mock function.

        Returns:
            None
        """
        all_recipes = pd.DataFrame({
            'name': ['Recipe1', 'Recipe2'],
            'nutriscore': [50, 45],
            'label': ['A', 'B'],
            'tags': ['tag1', 'tag2']
        })
        label_choice = 'A'
        app.display_datatable(all_recipes, label_choice)
        
        mock_st.assert_called_once()
        dffilter = all_recipes[all_recipes['label'] == label_choice][[
            'name', 'nutriscore', 'label', 'tags'
            ]]

        called_args, called_kwargs = mock_st.call_args
    
        pd.testing.assert_frame_equal(called_args[0], dffilter)
        self.assertEqual(called_kwargs.get('hide_index'), True)
        
        
    @patch('streamlit.markdown')
    @patch('streamlit.radio')
    @patch('streamlit.dataframe')
    def test_display_choosing_labels(self, 
                                     mock_dataframe, 
                                     mock_radio, 
                                     mock_markdown):
        """
        Test display_choosing_labels function.
        
        Agrs:
            mock_dataframe (MagicMock): Mock st.dataframe function.
            mock_radio (MagicMock): Mock st.radio function.
            mock_markdown (MagicMock): Mock st.markdown function.
            
        Returns:
            None
        """
        all_recipes_proccessed = pd.DataFrame({
            'id': [10, 20],
            'name': ['Recipe1', 'Recipe2'],
            'nutriscore': [50, 45],
            'label': ['A', 'B'],
            'tags': ['tag1', 'tag2']
        })
        all_recipes = all_recipes_proccessed.copy()

        mock_radio.return_value = 'A'

        app.display_choosing_labels(all_recipes_proccessed, all_recipes)

        mock_markdown.assert_called()
        mock_radio.assert_called_once()
        
        expected_dataframe = all_recipes_proccessed[
            all_recipes_proccessed['label'] == 'A'
        ][['name', 'nutriscore', 'label', 'tags']]

        pd.testing.assert_frame_equal(
            mock_dataframe.call_args[0][0], 
            expected_dataframe
        )
        self.assertEqual(mock_dataframe.call_args[1].get('hide_index'), True)


    @patch('streamlit.table')
    def test_display_statistical_description(self, mock_st):
        """
        Test display_statistical_description function.

        Args:
            mock_st (MagicMock): Mock st.table function.

        Returns:
            None
        """
        processed_recipes = pd.DataFrame({
            'id': [10, 20, 30],
            'name': ['Recipe1', 'Recipe2', 'Recipe3'],
            'label': ['A', 'A', 'B'],
            'dv_calories_%': [50, 60, 40],
            'dv_protein_%': [20, 30, 25]
        })
        choix = 'A'

        result = app.display_statistical_description(processed_recipes, choix)
        
        self.assertIn('mean', result.columns)
        self.assertIn('std', result.columns)
        self.assertEqual(len(result), 2) 


    @patch('streamlit.write')
    @patch('streamlit.subheader')
    @patch('streamlit.dataframe')

    def test_select_to_process(self, 
                               mock_write, 
                               mock_subheader, 
                               mock_dataframe):
        """
        Test select_to_process function.
        
        Args:
            mock_write (MagicMock): Mock st.write function.
            mock_subheader (MagicMock): Mock st.subheader function.
            mock_dataframe (MagicMock): Mock st.dataframe function.

        Returns:
            None
        """
        all_recipes = pd.DataFrame({
            'name': ['Recipe1', 'Recipe2'],
            'nutriscore': [50, 45],
            'label': ['A', 'B'],
            'tags': ['tag1', 'tag2']
        })
        all_recipes_proccessed = all_recipes.copy()
        highest_recipes = all_recipes.copy()
        tags_input = "tag1"


        app.select_to_process(all_recipes, 
                              all_recipes_proccessed, 
                              highest_recipes, 
                              tags_input)

        mock_write.assert_called()
        mock_subheader.assert_called()
        mock_dataframe.assert_called()
    
    @patch('streamlit.plotly_chart')
    def test_display_bar_chart(self, mock_plotly_chart):
        """
        Test display_bar_chart function.
        
        Args:
            mock_plotly_chart (MagicMock): Mock st.plotly_chart function.
        
        Returns:
            None
        """
        stats = pd.DataFrame({
            'mean': [20, 30, 25, 14, 80], 
            'std': [5, 10, 8, 3, 12],
            'min': [15, 20, 18, 10, 70],
            'max': [25, 40, 30, 24, 90]
        }, index=['calories', 'protein', 'fat', 'sodium', 'nutriscore'])

        app.display_bar_chart(stats)

        mock_plotly_chart.assert_called_once()

        fig = mock_plotly_chart.call_args[0][0]

        self.assertEqual(
            fig.layout.title.text,
            'Nutrition of the recipes on bar chart with the selected label'
        )

    @patch('streamlit.write')
    @patch('tags_nutriscore_correlation.main')
    @patch('streamlit.multiselect')
    @patch('streamlit.columns')
    @patch('streamlit.markdown')
    @patch('streamlit.set_page_config')
    def test_main(self, 
                mock_set_page_config, 
                mock_markdown, 
                mock_columns, 
                mock_multiselect, 
                mock_tags_nutriscore_main, 
                mock_write):
        """
        Test main function.
        
        Returns:
            None
        """
        
        mock_multiselect.return_value = ['course']
        mock_tags_nutriscore_main.return_value = (
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        )
        mock_columns.return_value = (MagicMock(), MagicMock())

        app.main()

        mock_set_page_config.assert_called_once_with(layout="centered")
        mock_markdown.assert_called()
        mock_multiselect.assert_called_once()
        mock_tags_nutriscore_main.assert_called_once()

if __name__ == "__main__":
    unittest.main()

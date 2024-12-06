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

# Import module 6_Appendix.py
spec = importlib.util.spec_from_file_location(
    "module_5_TagAnalysis",
    os.path.join(os.path.dirname(__file__),
                 '../src/pages/5_TagAnalysis.py')
)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class TestRecipesApp(unittest.TestCase):

    @patch('streamlit.dataframe')
    def test_display_datatable(self, mock_st):
        """
        Test de la fonction display_datatable.

        Args:
            mock_st (MagicMock): Mock de la fonction st.dataframe

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
        # Vérification que les données sont filtrées correctement et affichées
        mock_st.assert_called_once()
        dffilter = all_recipes[all_recipes['label'] == label_choice][[
            'name', 'nutriscore', 'label', 'tags'
            ]]
        # Extraire l'argument réel utilisé avec le mock
        called_args, called_kwargs = mock_st.call_args
    
        # Vérifier que l'argument passé est équivalent au DataFrame attendu
        pd.testing.assert_frame_equal(called_args[0], dffilter)

        # Vérifier les autres arguments
        self.assertEqual(called_kwargs.get('hide_index'), True)
        
        
    @patch('streamlit.markdown')
    @patch('streamlit.radio')
    @patch('streamlit.dataframe')
    def test_display_choosing_labels(self, 
                                     mock_dataframe, 
                                     mock_radio, 
                                     mock_markdown):
        """
        Test de la fonction display_choosing_labels.
        
        Agrs:
            mock_dataframe (MagicMock): Mock de la fonction st.dataframe
            mock_radio (MagicMock): Mock de la fonction st.radio
            mock_markdown (MagicMock): Mock de la fonction st.markdown
            
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
        #all_recipes = all_recipes_proccessed.all()
        all_recipes = all_recipes_proccessed.copy()

        # Configurer le mock pour st.radio
        mock_radio.return_value = 'A'

        # Appeler la fonction display_choosing_labels
        app.display_choosing_labels(all_recipes_proccessed, all_recipes)

        # Vérifier que les fonctions Streamlit ont été appelées correctement
        mock_markdown.assert_called()
        mock_radio.assert_called_once()
        
        # DataFrame attendu après filtrage
        expected_dataframe = all_recipes_proccessed[
            all_recipes_proccessed['label'] == 'A'
        ][['name', 'nutriscore', 'label', 'tags']]

        # Vérification de l'appel à mock_dataframe
        pd.testing.assert_frame_equal(
            mock_dataframe.call_args[0][0], 
            expected_dataframe
        )
        self.assertEqual(mock_dataframe.call_args[1].get('hide_index'), True)


    @patch('streamlit.table')
    def test_display_statistical_description(self, mock_st):
        """
        Test de la fonction display_statistical_description.

        Args:
            mock_st (MagicMock): Mock de la fonction st.table

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
        
        # Vérification que la sortie est correcte
        self.assertIn('mean', result.columns)
        self.assertIn('std', result.columns)
        self.assertEqual(len(result), 2)  # Deux colonnes nutritionnelles


    @patch('streamlit.write')
    @patch('streamlit.subheader')
    @patch('streamlit.dataframe')
    # def test_select_to_process(self, mock_main, mock_st):
    def test_select_to_process(self, 
                               mock_write, 
                               mock_subheader, 
                               mock_dataframe):
        """
        Test de la fonction select_to_process.
        
        Args:
            mock_write (MagicMock): Mock de la fonction st.write
            mock_subheader (MagicMock): Mock de la fonction st.subheader
            mock_dataframe (MagicMock): Mock de la fonction st.dataframe

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

        # mock_main.return_value = (all_recipes, 
        #                           all_recipes_proccessed, 
        #                           highest_recipes)

        app.select_to_process(all_recipes, 
                              all_recipes_proccessed, 
                              highest_recipes, 
                              tags_input)

        # Vérifier que st.write a été appelé
        mock_write.assert_called()
        mock_subheader.assert_called()
        mock_dataframe.assert_called()
    
    @patch('streamlit.plotly_chart')
    def test_display_bar_chart(self, mock_plotly_chart):
        """
        Test de la fonction display_bar_chart.
        
        Args:
            mock_plotly_chart (MagicMock): Mock de la fonction st.plotly_chart
        
        Returns:
            None
        """
        stats = pd.DataFrame({
            'mean': [20, 30, 25, 14, 80], 
            'std': [5, 10, 8, 3, 12],
            'min': [15, 20, 18, 10, 70],
            'max': [25, 40, 30, 24, 90]
        }, index=['calories', 'protein', 'fat', 'sodium', 'nutriscore'])

        # Appeler la fonction display_bar_chart
        app.display_bar_chart(stats)

        # Vérification que la fonction de Streamlit pour afficher 
        # les graphiques est appelée
        mock_plotly_chart.assert_called_once()

        # Récupérer l'argument passé à st.plotly_chart
        fig = mock_plotly_chart.call_args[0][0]

        # Vérification du titre de la figure
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
        Test de la fonction main.
        
        Returns:
            None
        """
        
        # Configurer les mocks
        mock_multiselect.return_value = ['course']
        mock_tags_nutriscore_main.return_value = (
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        )
        mock_columns.return_value = (MagicMock(), MagicMock())

        # Appeler la fonction main
        app.main()

        # Vérifier que les fonctions Streamlit ont été appelées correctement
        mock_set_page_config.assert_called_once_with(layout="centered")
        mock_markdown.assert_called()
        mock_multiselect.assert_called_once()
        mock_tags_nutriscore_main.assert_called_once()

if __name__ == "__main__":
    unittest.main()

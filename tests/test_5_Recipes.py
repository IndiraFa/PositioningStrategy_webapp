import sys,os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import tags_nutriscore_correlation
import importlib.util

# Import module 6_Appendix.py
spec = importlib.util.spec_from_file_location(
    "app",
    os.path.join(os.path.dirname(__file__),
                 '../src/pages/5_Appendix.py')
)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module_5_Appendix)


class TestRecipesApp(unittest.TestCase):

    @patch('streamlit.dataframe')
    @patch('tags_nutriscore_correlation.main')
    def test_display_top10recipes(self, mock_main, mock_st):
        """Test de la fonction display_top10recipes."""
        all_recipes = pd.DataFrame({
            'name': ['Recipe1', 'Recipe2'],
            'nutriscore': [50, 45],
            'label': ['A', 'B'],
            'tags': ['tag1', 'tag2']
        })
        highest_recipes = all_recipes.copy()
        tags_input = "tag1"
        
        # Appeler la fonction
        app.display_top10recipes(all_recipes, highest_recipes, tags_input)

        # Vérification que Streamlit a affiché les bonnes données
        mock_st.markdown.assert_called()
        mock_st.dataframe.assert_called_with(highest_recipes[['name', 'nutriscore', 'label', 'tags']].head(10), hide_index=True)

    @patch('streamlit.dataframe')
    def test_display_datatable(self, mock_st):
        """Test de la fonction display_datatable."""
        all_recipes = pd.DataFrame({
            'name': ['Recipe1', 'Recipe2'],
            'nutriscore': [50, 45],
            'label': ['A', 'B'],
            'tags': ['tag1', 'tag2']
        })
        label_choice = 'A'
        
        app.display_datatable(all_recipes, label_choice)

        # Vérification que les données sont filtrées correctement et affichées
        mock_st.dataframe.assert_called()

    @patch('5_Recipes.st')
    def test_display_statistical_description(self, mock_st):
        """Test de la fonction display_statistical_description."""
        processed_recipes = pd.DataFrame({
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

    @patch('pandas.DataFrame')
    def test_display_pie_chart(self, mock_st):
        """Test de la fonction display_pie_chart."""
        stats = pd.DataFrame({
            'mean': [20, 30, 25],
            'std': [5, 10, 8],
            'min': [15, 20, 18],
            'max': [25, 40, 30]
        }, index=['calories', 'protein', 'fat'])

        app.display_pie_chart(stats)

        # Vérification que la fonction de Streamlit pour afficher les graphiques est appelée
        mock_st.plotly_chart.assert_called()

    @patch('5_Recipes.st')
    @patch('tags_nutriscore_correlation.main')
    def test_select_to_process(self, mock_main, mock_st):
        """Test de la fonction select_to_process."""
        all_recipes = pd.DataFrame({
            'name': ['Recipe1', 'Recipe2'],
            'nutriscore': [50, 45],
            'label': ['A', 'B'],
            'tags': ['tag1', 'tag2']
        })
        all_recipes_proccessed = all_recipes.copy()
        highest_recipes = all_recipes.copy()
        tags_input = "tag1"

        mock_main.return_value = (all_recipes, all_recipes_proccessed, highest_recipes)

        app.select_to_process(all_recipes, all_recipes_proccessed, highest_recipes, tags_input)

        # Vérification que certaines fonctions clés ont été appelées
        mock_st.write.assert_called()
        mock_st.subheader.assert_called()

if __name__ == "__main__":
    unittest.main()

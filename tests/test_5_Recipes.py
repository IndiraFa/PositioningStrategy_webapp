import sys,os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import tags_nutriscore_correlation
import importlib.util

# Import module 6_Appendix.py
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
        mock_st.assert_called_once()
        dffilter = all_recipes[all_recipes['label'] == label_choice].any()[['name', 'nutriscore', 'label', 'tags']]
        mock_st.assert_called_with(dffilter, hide_index=True)

    @patch('streamlit.markdown')
    @patch('streamlit.radio')
    @patch('streamlit.dataframe')
    def test_display_choosing_labels(self, mock_dataframe, mock_radio, mock_markdown):
        """Test de la fonction display_choosing_labels."""
        all_recipes_proccessed = pd.DataFrame({
            'id': [10, 20],
            'name': ['Recipe1', 'Recipe2'],
            'nutriscore': [50, 45],
            'label': ['A', 'B'],
            'tags': ['tag1', 'tag2']
        })
        all_recipes = all_recipes_proccessed.all()

        # Configurer le mock pour st.radio
        mock_radio.return_value = 'A'

        # Appeler la fonction display_choosing_labels
        app.display_choosing_labels(all_recipes_proccessed, all_recipes)

        # Vérifier que les fonctions Streamlit ont été appelées correctement
        mock_markdown.assert_called()
        mock_radio.assert_called_once()
        mock_dataframe.assert_called_with(all_recipes_proccessed[all_recipes_proccessed['label'] == 'A'][['name', 'nutriscore', 'label', 'tags']], hide_index=True)

    @patch('streamlit.table')
    def test_display_statistical_description(self, mock_st):
        """Test de la fonction display_statistical_description."""
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

    @patch('streamlit.plotly_chart')
    def test_display_pie_chart(self, mock_plotly_chart):
        """Test de la fonction display_pie_chart."""
        stats = pd.DataFrame({
            'mean': [20, 30, 25, 14],
            'std': [5, 10, 8, 3],
            'min': [15, 20, 18, 10],
            'max': [25, 40, 30, 24]
        }, index=['calories', 'protein', 'fat', 'nutriscore'])

        # Appeler la fonction display_pie_chart
        app.display_pie_chart(stats)

        # Vérification que la fonction de Streamlit pour afficher les graphiques est appelée
        mock_plotly_chart.assert_called_once()

    @patch('streamlit.write')
    @patch('streamlit.subheader')
    @patch('streamlit.dataframe')
    # def test_select_to_process(self, mock_main, mock_st):
    def test_select_to_process(self, mock_write, mock_subheader, mock_dataframe):
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

        # mock_main.return_value = (all_recipes, all_recipes_proccessed, highest_recipes)

        app.select_to_process(all_recipes, all_recipes_proccessed, highest_recipes, tags_input)

        # Vérifier que st.write a été appelé
        mock_write.assert_called()
        mock_subheader.assert_called()
        mock_dataframe.assert_called()

if __name__ == "__main__":
    unittest.main()

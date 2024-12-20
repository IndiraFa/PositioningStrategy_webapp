import os
import sys
import pytest
import unittest
from unittest.mock import patch
import pandas as pd

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'src')
    )
)

from tags_nutriscore_correlation import (
    Utils,
    PreprocessTags,
    Tags,
    DatabaseTable,
    load_streamlit_db,
    main
)


# Exemple de données fictives
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'id': [1, 2, 3],
        'tags': ["['30-minutes-or-less', 'time-to-make', 'course']",
                 "['60-minutes-or-less', 'time-to-make']",
                 "['90-minutes-or-less', 'main-ingredient', 'course','meat']"]
    })


@pytest.fixture
def formatted_tags_data():
    return pd.DataFrame({
        'idrecipes': [1, 1, 1, 2, 2, 3, 3, 3, 3],
        'tags': ['30 minutes or less', 'time to make', 'course',
                 '60 minutes or less', 'time to make',
                 '90 minutes or less', 'main ingredient', 'course', 'meat']
    })


# Tests pour Utils
def test_get_value_from_string():
    assert Utils.get_value_from_string("abc123") == [123]
    assert Utils.get_value_from_string("45.67xyz") == [45.67]
    assert Utils.get_value_from_string("no numbers") == []


def test_get_text_from_string():
    assert Utils.get_text_from_string(
        "['30-minutes-or-less', 'time-to-make', 'course', 'meat']"
        ) == ['30-minutes-or-less', 'time-to-make', 'course', 'meat']
    # assert Utils.get_text_from_string("No-Tags!") == ['No', 'Tags']


# Tests pour PreprocessTags
def test_preprocess_tags_split(sample_data):
    preprocessor = PreprocessTags(sample_data)
    expected_tags = [
        ['30 minutes or less', 'time to make', 'course'],
        ['60 minutes or less', 'time to make'],
        ['90 minutes or less', 'main ingredient', 'course', 'meat']]
    assert preprocessor.split_text_tag() == expected_tags


def test_formatter_tags_data(sample_data, formatted_tags_data):
    preprocessor = PreprocessTags(sample_data)
    formatted = preprocessor.formatter_tags_data()
    pd.testing.assert_frame_equal(formatted, formatted_tags_data)


# Tests pour Tags
def test_extract_tag(formatted_tags_data):
    tag_handler = Tags(formatted_tags_data, 'course')
    ids = tag_handler.extract_tag('course')
    assert (ids == [1, 3]).all()


def test_get_recipes_from_tags_single_tag(formatted_tags_data):
    tag_handler = Tags(formatted_tags_data, 'course')
    ids = tag_handler.get_recipes_from_tags()
    assert (ids == [1, 3]).all()


def test_get_recipes_from_tags_multiple_tags(formatted_tags_data):
    tag_handler = Tags(formatted_tags_data, 'course,meat')
    ids = tag_handler.get_recipes_from_tags()
    assert ids == [3]


def test_database_table_init():
    """Test du constructeur de la classe DatabaseTable."""

    # Créer une instance de DatabaseTable
    table_name = 'test_table'
    query = 'SELECT * FROM test_table;'
    data = None
    db_table = DatabaseTable(table_name, query, data)

    # Vérifier que les attributs sont correctement initialisés
    assert db_table.table_name == table_name
    assert db_table.query == query
    assert db_table.data == data


class TestDatabaseTable(unittest.TestCase):

    @patch('tags_nutriscore_correlation.db_instance.fetch_data')
    def test_load_streamlit_db(self, mock_fetch_data):
        """Test de la fonction load_streamlit_db."""

        # Configurer le mock pour retourner un DataFrame simulé
        mock_fetch_data.return_value = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Recipe1', 'Recipe2', 'Recipe3'],
            'tags': ['tag1', 'tag2', 'tag3']
        })

        # Appeler la fonction load_streamlit_db
        result = load_streamlit_db('raw_recipes')

        # Vérifier que fetch_data a été appelé avec la bonne requête
        mock_fetch_data.assert_called_once_with('SELECT * FROM "raw_recipes";')

        # Vérifier que le résultat est un DataFrame et
        # contient les données attendues
        expected_result = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Recipe1', 'Recipe2', 'Recipe3'],
            'tags': ['tag1', 'tag2', 'tag3']
        })
        pd.testing.assert_frame_equal(result, expected_result)

    @patch('tags_nutriscore_correlation.load_streamlit_db')
    def test_apply_streamlit_db(self, mock_load_streamlit_db):
        """Test de la méthode apply_streamlit_db."""

        # Configurer le mock pour load_streamlit_db
        mock_load_streamlit_db.return_value = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Recipe1', 'Recipe2', 'Recipe3'],
            'tags': ['tag1', 'tag2', 'tag3']
        })

        # Créer une instance de DatabaseTable
        table_name = 'test_table'
        query = 'SELECT * FROM test_table;'
        db_table = DatabaseTable(table_name, query)

        # Appeler la méthode apply_streamlit_db
        result = db_table.apply_streamlit_db()

        # Vérifier que load_streamlit_db a été appelé avec les bons arguments
        mock_load_streamlit_db.assert_called_once_with(table_name, query)

        # Vérifier que le résultat est un DataFrame et
        # contient les données attendues
        expected_result = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Recipe1', 'Recipe2', 'Recipe3'],
            'tags': ['tag1', 'tag2', 'tag3']
        })
        pd.testing.assert_frame_equal(result, expected_result)


@patch('tags_nutriscore_correlation.DatabaseTable.apply_streamlit_db')
@patch('tags_nutriscore_correlation.Tags.get_recipes_from_tags')
def test_main(mock_get_recipes_from_tags, mock_apply_streamlit_db):
    """Test de la fonction main."""

    # Configurer les mocks pour retourner des DataFrames simulés
    mock_apply_streamlit_db.side_effect = [
        pd.DataFrame({
            'name': ['Recipe1', 'Recipe2', 'Recipe3'],
            'id': [1, 2, 3],
            'tags': ['tag1', 'tag2', 'tag3']
        }),
        pd.DataFrame({
            'id': [1, 2, 3],
            'nutriscore': [50, 45, 40],
            'label': ['A', 'B', 'C']
        }),
        pd.DataFrame({
            'tags': ['tag1', 'tag2', 'tag3'],
            'idrecipes': [1, 2, 3]
        })
    ]

    mock_get_recipes_from_tags.return_value = [1, 2]

    # Appeler la fonction main
    tags_reference = 'tag1,tag2'
    recipes_tags, dfsortinner, recipes_highestscore = main(tags_reference)

    # Vérifier les résultats
    expected_recipes_tags = pd.DataFrame({
        'name': ['Recipe1', 'Recipe2'],
        'id': [1, 2],
        'tags': ['tag1', 'tag2'],
        'nutriscore': [50, 45],
        'label': ['A', 'B']
    })
    expected_dfsortinner = pd.DataFrame({
        'id': [1, 2],
        'nutriscore': [50, 45],
        'label': ['A', 'B'],
        'name': ['Recipe1', 'Recipe2']
    })
    expected_recipes_highestscore = pd.DataFrame({
        'name': ['Recipe1'],
        'id': [2],
        'tags': ['tag2'],
        'nutriscore': [45],
        'label': ['B']
    }).head(10)

    pd.testing.assert_frame_equal(recipes_tags, expected_recipes_tags)
    pd.testing.assert_frame_equal(dfsortinner, expected_dfsortinner)
    # pd.testing.assert_frame_equal(recipes_highestscore,
    #                               expected_recipes_highestscore)


if __name__ == '__main__':
    unittest.main()
import pytest
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from tags_nutriscore_correlation import Utils, PreprocessTags, Tags

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

### Tests pour Utils
def test_get_value_from_string():
    assert Utils.get_value_from_string("abc123") == [123]
    assert Utils.get_value_from_string("45.67xyz") == [45.67]
    assert Utils.get_value_from_string("no numbers") == []

def test_get_text_from_string():
    assert Utils.get_text_from_string(
        "['30-minutes-or-less', 'time-to-make', 'course', 'meat']"
        ) == ['30-minutes-or-less', 'time-to-make', 'course','meat']
    # assert Utils.get_text_from_string("No-Tags!") == ['No', 'Tags']

### Tests pour PreprocessTags
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

### Tests pour Tags
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

import os
import sys
import pytest
from unittest.mock import patch
from core.asset_manager import get_asset_path

# Add the 'src' directory to the system path for importing modules
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
)
@pytest.fixture
def mock_base_dir():
    """
    Fixture to mock the base directory path for testing.
    """
    return "/mock/project/root"


@patch("core.asset_manager.os.path.dirname")
@patch("core.asset_manager.os.path.abspath")
def test_get_asset_path(mock_abspath, mock_dirname, mock_base_dir):
    """
    Test that the `get_asset_path` function correctly constructs the absolute path.

    This test ensures that the function computes the path by navigating 
    three levels up and appending the `assets` directory and the file path.
    """
    # Mock the base directory path
    mock_abspath.return_value = f"{mock_base_dir}/core/asset_manager.py"
    
    # Simulate `os.path.dirname` behavior by providing mock return values
    mock_dirname.side_effect = [
        f"{mock_base_dir}/core",
        f"{mock_base_dir}/",
        mock_base_dir
    ]

    # File path to locate in the assets directory
    relative_file_path = "images/test_image.png"
    expected_path = f"{mock_base_dir}/assets/{relative_file_path}"

    # Call the function under test
    result = get_asset_path(relative_file_path)

    # Assertions
    assert result == expected_path, f"Expected path {expected_path}, but got {result}"


@patch("core.asset_manager.logger")
@patch("core.asset_manager.os.path.join")
def test_get_asset_path_logs(mock_path_join, mock_logger):
    """
    Test that the `get_asset_path` function logs the computed asset path.

    This test ensures that the logger outputs the correct debug message
    for the computed path.
    """
    # Mock the join result
    mock_path_join.return_value = "/mock/project/root/assets/images/test_image.png"

    # Call the function under test
    get_asset_path("images/test_image.png")

    # Verify that the logger logged the correct path
    mock_logger.debug.assert_called_once_with("Asset path: /mock/project/root/assets/images/test_image.png")

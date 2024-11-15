import os
import pytest
from unittest.mock import patch, MagicMock
from utils.data_loader import validate_url, download_data, load_data

# 1. Tests for `validate_url`
@patch("utils.data_loader.logger")
def test_validate_url_valid(mock_logger):
    # Check that a valid URL returns True
    assert validate_url("http://example.com") is True
    mock_logger.error.assert_not_called()

@patch("utils.data_loader.logger")
def test_validate_url_empty(mock_logger):
    # Check that an empty URL returns False and logs an error message
    assert validate_url("") is False
    mock_logger.error.assert_called_once_with("The download link is not defined in the .env file.")

@patch("utils.data_loader.logger")
def test_validate_url_invalid(mock_logger):
    # Check that an invalid URL returns False and logs an error message
    assert validate_url("invalid_url") is False
    mock_logger.error.assert_called_once_with("The download link is not a valid URL.")

# 2. Tests for `download_data`
@patch("utils.data_loader.requests.get")
@patch("utils.data_loader.logger")
def test_download_data_success(mock_logger, mock_get):
    # Mock a successful HTTP request response for download
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake content"
    mock_get.return_value = mock_response

    url = "http://example.com/fakefile.txt"
    output_dir = "test_datasets"

    # Mock the open function and simulate the write method
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Execute download_data
        file_path = download_data(url, output_dir)
        
        # Check that the file path is as expected and requests and open functions were called
        assert file_path == os.path.join(output_dir, "fakefile.txt")
        mock_get.assert_called_once_with(url)
        mock_open.assert_called_once_with(file_path, "wb")
        mock_file.write.assert_called_once_with(b"fake content")
        mock_logger.info.assert_called_with(f"Download completed successfully. File saved as {file_path}")
@patch("utils.data_loader.requests.get")
@patch("utils.data_loader.logger")
def test_download_data_failure(mock_logger, mock_get):
    # Mock an HTTP request failure with status code 404
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    url = "http://example.com/fakefile.txt"
    output_dir = "test_datasets"

    # Execute `download_data` function
    file_path = download_data(url, output_dir)

    # Assert that None is returned on failure and an error is logged
    assert file_path is None
    mock_get.assert_called_once_with(url)
    mock_logger.error.assert_called_once_with("Error while downloading, status: 404")

# 3. Tests for `load_data`
@patch("utils.data_loader.download_data")
@patch("utils.data_loader.validate_url")
@patch("utils.data_loader.os.getenv")
def test_load_data(mock_getenv, mock_validate_url, mock_download_data):
    # Configure environment variables and mock return values
    mock_getenv.side_effect = lambda var_name, default=None: "http://example.com/file1.txt, http://example.com/file2.txt" if var_name == "DRIVE_LINKS" else "test_datasets"
    mock_validate_url.side_effect = [True, True]
    mock_download_data.side_effect = [os.path.join("test_datasets", "file1.txt"), os.path.join("test_datasets", "file2.txt")]

    # Execute `load_data` function
    load_data()

    # Assert that `validate_url` and `download_data` were called for each URL
    mock_validate_url.assert_any_call("http://example.com/file1.txt")
    mock_validate_url.assert_any_call("http://example.com/file2.txt")
    mock_download_data.assert_any_call("http://example.com/file1.txt", "test_datasets")
    mock_download_data.assert_any_call("http://example.com/file2.txt", "test_datasets")

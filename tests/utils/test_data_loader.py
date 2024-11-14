import unittest
import io
import os
from unittest.mock import mock_open, patch, MagicMock
from utils.data_loader import validate_url, download_data, extract_files

class TestDataLoader(unittest.TestCase):
    @patch("data_loader.logger")
    def test_validate_url(self, mock_logger):
        # Test with a valid URL
        self.assertTrue(validate_url("http://example.com"))
        
        # Test with an empty URL
        self.assertFalse(validate_url(""))
        mock_logger.error.assert_called_with("The download link is not defined in the .env file.")
        
        # Test with an invalid URL
        self.assertFalse(validate_url("invalid_url"))
        mock_logger.error.assert_called_with("The download link is not a valid URL.")

    def test_download_data(self, mock_logger, mock_get):
        # simulate a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake data"
        mock_get.return_value = mock_response

        archive = download_data("https://example.com")
        self.assertIsInstance(archive, io.BytesIO)
        mock_logger.info.assert_called_with("Download completed successfully")


        # simulate a failed response
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        archive = download_data("https://example.com")
        self.assertIsNone(archive)
        mock_logger.error.assert_called_with("Error while downloading, status: 404")



if __name__ == "__main__":
    unittest.main()
import os
import io
import logging
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement depuis config.env
load_dotenv()

logger = logging.getLogger("app.utils.data_loader")

def validate_url(url):
    """Check if the provided URL is valid."""
    if not url:
        logger.error("The download link is not defined in the .env file.")
        return False
    if not url.startswith("http"):
        logger.error("The download link is not a valid URL.")
        return False
    return True

def download_data(url, output_dir="src/datasets"):
    """
    Download data from the specified URL and save it to the output directory.

    Args:
        url (str): The URL to download the file from.
        output_dir (str): The directory where the downloaded file will be saved.

    Returns:
        str: The path to the downloaded file if successful, None otherwise.
    """
    try:
        logger.info(f"Downloading dataset from {url}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            # Extract filename from URL and create full path
            filename = os.path.basename(url)
            file_path = os.path.join(output_dir, filename)

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Save the file content to the specified path
            with open(file_path, "wb") as file:
                file.write(response.content)
            
            logger.info(f"Download completed successfully. File saved as {file_path}")
            return file_path
        else:
            logger.error(f"Error while downloading, status: {response.status_code}")
            return None
    except requests.exceptions.RequestException as ex:
        logger.error(f"Request failed: {ex}")
        return None

def load_data():
    """
    Loads data from multiple URLs specified in environment variables and saves them to the output directory.
    
    Expects environment variables:
        - DRIVE_LINKS (str): A comma-separated list of URLs to download.
        - OUTPUT_DIR (str): The directory where downloaded files will be saved, defaulting to "src/datasets".
    """
    # Load environment variables
    urls = os.getenv("DRIVE_LINKS")
    output_dir = os.getenv("OUTPUT_DIR", "src/datasets")

    if not urls:
        logger.error("No download links provided in the environment variables.")
        return

    # Split URLs if multiple links are provided
    urls = [url.strip() for url in urls.split(",")]

    for url in urls:
        # Validate each URL
        if not validate_url(url):
            continue

        # Download each file
        download_data(url, output_dir)

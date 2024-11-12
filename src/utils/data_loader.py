import logging
import requests
import zipfile
import os
import io
from dotenv import load_dotenv

# load environment variables from config.env
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

def extract_files(archive, output_dir):
    """Extract files in the 'recipe' folder from the archive into the specified output directory."""
    try:
        # Create the output directory if it does not exist
        os.makedirs(output_dir, exist_ok=True)
        
        with zipfile.ZipFile(archive) as z:
            recipe_files = [f for f in z.namelist() if f.startswith("recipe/")]
            if recipe_files:
                for file in recipe_files:
                    z.extract(file, output_dir)
                
                # Validate extracted files
                extracted_paths = [os.path.join(output_dir, file) for file in recipe_files]
                missing_files = [file for file in extracted_paths if not os.path.exists(file)]
                
                if missing_files:
                    logger.warning(f"Some files were not extracted correctly: {missing_files}")
                else:
                    logger.info(f"{len(recipe_files)} files extracted in '{output_dir}/recipe'.")
            else:
                logger.warning("No files found in the ‘recipe’ folder in the archive.")
    except zipfile.BadZipFile as ex:
        logger.error(f"Failed to extract files: Invalid ZIP archive. {ex}")
    except Exception as ex:
        logger.error(f"An error occurred during extraction: {ex}")


def download_data(url):
    """Download data from the specified URL."""
    try:
        logger.info("Downloading dataset...")
        response = requests.get(url)
        
        if response.status_code == 200:
            logger.info("Download completed successfully.")
            return io.BytesIO(response.content)
        else:
            logger.error(f"Error while downloading, status: {response.status_code}")
            return None
    except requests.exceptions.RequestException as ex:
        logger.error(f"Request failed: {ex}")
        return None

def load_data():
    """
    Loads and extracts data from a specified URL in the environment variables.
    Downloads a ZIP file from the DRIVE_LINK and extracts files in the 'recipe' folder into OUTPUT_DIR.
    """
    # Load environment variables
    url = os.getenv("DRIVE_LINK")
    output_dir = os.getenv("OUTPUT_DIR", "src/datasets")

    # Validate the URL
    if not validate_url(url):
        return

    # Download data
    archive = download_data(url)
    if archive is None:
        logger.error("Data download failed.")
        return

    # Extract files
    extract_files(archive, output_dir)
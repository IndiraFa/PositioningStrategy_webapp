import logging
import os

logger = logging.getLogger("core.asset_manager")


def get_asset_path(file_path: str) -> str:
    """
    Retrieve the absolute path to a file located in the assets directory.

    This function constructs the full path to a file within the `assets` directory 
    relative to the base directory of the project. The base directory is computed 
    as the third parent directory of the current file.

    Args:
        file_path (str): The relative path of the file within the `assets` directory.

    Returns:
        str: The absolute path to the specified file in the `assets` directory.
    """
    # Calculate the base directory (third parent of the current file)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Build the absolute path to the target file in the assets directory
    asset_path = os.path.join(base_dir, "assets", file_path)

    # Log the computed path for debugging purposes
    logger.debug(f"Asset path: {asset_path}")

    return asset_path

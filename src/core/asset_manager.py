import logging
import os

logger = logging.getLogger("core.asset_manager")

def get_asset_path(file_path):
    """
    Get the absolute path to a file in the assets directory.

    Args:
        file_path (str): Relative path to the file within the assets directory.

    Returns:
        str: Absolute path to the file.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logger.debug(f"asset path: {os.path.join(base_dir, "assets", file_path)}")
    return os.path.join(base_dir, "assets", file_path)
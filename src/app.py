import streamlit as st
from utils.config_logging import configure_logging

# Initialize logging
logger = configure_logging()

def main():
    logger.info("Streamlit App is starting")
    st.title("Mangetamain Web App")


if __name__ == "__main__":
    main()
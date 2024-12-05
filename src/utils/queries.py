# utils/queries.py

QUERIES = {
    ## Homepage Query
    "with_outliers": """
        SELECT * FROM "NS_withOutliers";
    """,
    "no_outliers": """
        SELECT * FROM "NS_noOutliers";
    """
}

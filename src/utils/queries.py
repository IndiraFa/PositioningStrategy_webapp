query_with_outliers = """
SELECT * FROM "NS_withOutliers";
"""

query_no_outliers = """
SELECT * FROM "NS_noOutliers";
"""

query_raw_interaction = """
SELECT * FROM "RAW_interactions";
"""

query_filtered_data = """
SELECT 
    ns.id,
    ns."dv_calories_%",
    ns."dv_total_fat_%",
    ns."dv_sugar_%",
    ns."dv_sodium_%",
    ns."dv_protein_%",
    ns."dv_sat_fat_%",
    ns."dv_carbs_%",
    ns."nutriscore",
    rr."minutes",
    rr."n_steps",
    rr."n_ingredients"
FROM "raw_recipes" rr 
INNER JOIN "NS_noOutliers" ns 
ON rr.id=ns.id;
"""

import pandas as pd
import json

with open("tidy_product.json_mk1", "r") as f:
    mk1_data = json.load(f)

with open("tidy_product.json_sf6", "r") as f:
    sf6_data = json.load(f)

def build_comparison_row(data):
    """Builds a comparison row for the DataFrame based on the tidy JSON data."""
    r7 = data.get("rating_7_days", {}).get("RatingCount", 0)
    r30 = data.get("rating_30_days", {}).get("RatingCount", 0)
    
    # Calculations 
    momentum = (r7 / r30 * 100) if r30 > 0 else 0
    velocity = r7 / 7
    
    return {
        "Game Title": data.get("title"),
        "Business Model": "Game Pass" if data.get("has_gamepass_remediation") else "Paid",
        "7-Day Rating Count": r7,
        "30-Day Rating Count": r30,
        "Discovery Momentum (%)": round(momentum, 2),
        "Velocity (Ratings/Day)": round(velocity, 2),
        "All-Time Rating": data.get("rating_all_time", {}).get("AverageRating"),
        "Recent Rating (7d)": data.get("rating_7_days", {}).get("AverageRating"),
        "Recent Rating (30d)": data.get("rating_30_days", {}).get("AverageRating"),
    }

# 2. Create the DataFrame
comparison_list = [build_comparison_row(mk1_data), build_comparison_row(sf6_data)]
df = pd.DataFrame(comparison_list)

# 3. Save to CSV for your records
df.to_csv("gamepass_impact_report.csv", index=False)

print("--- Publisher Comparison Table ---")
print(df.to_string(index=False))
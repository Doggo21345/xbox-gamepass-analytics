import requests
import json

big_id = "9nm79b7n9jm6"
url = "https://displaycatalog.mp.microsoft.com/v7.0/products"
params = {
    "bigIds": big_id,
    "market": "US",
    "languages": "en-US",
}

r = requests.get(url, params=params, timeout=20)
print("STATUS:", r.status_code)

data = r.json()  # <-- THIS was missing

# (optional) save the full raw response so you can inspect it later
with open("raw_product_SF6.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

p = data["Products"][0]
lp = p["LocalizedProperties"][0]
mp = p["MarketProperties"][0]

tidy = {
    "product_id": p.get("ProductId"),
    "title": lp.get("ProductTitle"),
    "publisher": lp.get("PublisherName"),
    "developer": lp.get("DeveloperName"),
    "release_date": mp.get("OriginalReleaseDate"),
    "short_description": lp.get("ShortDescription"),
    "rating_all_time": (mp.get("UsageData") or [])[-1] if mp.get("UsageData") else None,
    "rating_7_days": (mp.get("UsageData") or [])[-3] if mp.get("UsageData") and len(mp.get("UsageData")) > 1 else None,
    "rating_30_days": (mp.get("UsageData") or [])[-2] if mp.get("UsageData") and len(mp.get("UsageData")) > 2 else None,
    "bundle_count": len(p.get("Properties", {}).get("BundledSkus", [])),
    "is_xpa": p.get("Properties", {}).get("XboxXPA", False),
    "platforms": p.get("Properties", {}).get("SupportedPlatforms", []),
    "asset_count": len(p.get("Images", [])) + len(p.get("Videos", [])),
    "has_gamepass_remediation": any(
    "Game Pass" in r.get("Description", "") 
    for lp_item in p.get("LocalizedProperties", [])
    for r in lp_item.get("EligibilityProperties", {}).get("Remediations", [])),
    "prices": [
        {
            "list_price": a.get("OrderManagementData", {}).get("Price", {}).get("ListPrice"),
            "msrp": a.get("OrderManagementData", {}).get("Price", {}).get("MSRP"),
            "start": a.get("Conditions", {}).get("StartDate"),
            "end": a.get("Conditions", {}).get("EndDate"),
        }

        for sku in p.get("DisplaySkuAvailabilities", [])
        for a in sku.get("Availabilities", [])
        if a.get("OrderManagementData", {}).get("Price")
    ]
}

with open("tidy_product.json_SF6", "w", encoding="utf-8") as f:
    json.dump(tidy, f, indent=2, ensure_ascii=False)

print("Wrote raw_product.json and tidy_product.json")

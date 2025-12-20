import requests
import json

big_id = "9N7358JZPX1Z"
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
with open("raw_product.json", "w", encoding="utf-8") as f:
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
    ],
    "trailers": [
        {
            "caption": v.get("Caption"),
            "hls": v.get("HLS"),
            "dash": v.get("DASH"),
        }
        for v in lp.get("CMSVideos", [])
    ],
    "images": [
        {
            "purpose": img.get("ImagePurpose"),
            "caption": img.get("Caption"),
            "url": ("https:" + img["Uri"]) if str(img.get("Uri", "")).startswith("//") else img.get("Uri"),
            "width": img.get("Width"),
            "height": img.get("Height"),
        }
        for img in lp.get("Images", [])
    ],
}

with open("tidy_product.json", "w", encoding="utf-8") as f:
    json.dump(tidy, f, indent=2, ensure_ascii=False)

print("Wrote raw_product.json and tidy_product.json")

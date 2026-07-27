import time
import requests

WEBHOOKS = {
    "RALPH LAUREN": "https://discordapp.com/api/webhooks/1530646409718665467/yTtKYkjF_SG50P4ayHCoZVbYaQs_eurzpUoQPylLdEJz0iFqFeHIVefni1nJyE2oaWez",
    "LACOSTE": "https://discordapp.com/api/webhooks/1531247162661408798/Cusmr3QgzzlcqxPDZhdwHtG04N91r-9u0W-YYYZ3RNnItg1JovTomlAdfAFqXfHnbWNg",
    "THE NORTH FACE": "https://discordapp.com/api/webhooks/1531247494556680243/DAqpUkexPS4ZbjJLNy5jicpEdS9pEQWcnTmEdJjbpnj4DApbJxUHdI8lh81w7npHl4Ix",
    "IPHONE": "https://discordapp.com/api/webhooks/1531247620683464747/zk0IKgd9VjLqHTO_kr3c3RwLZ97HC7f0itlW7SjY38JkzEvzHeS-1Sz-6p6sTpL8P7Hj",
    "LEGO": "https://discordapp.com/api/webhooks/1531247712656298098/KIAWVuLhf3snvoC8NNscUFMT6aiYOov8VaQO-syqRwZRr47k14_Hxk3VxNsTvatvaRju",
    "NIKE": "https://discordapp.com/api/webhooks/1531247346954801193/e7paMQkjanfpaunpKXL74pcAxMEastdyNYW68pMw7lIZ6koL7KOnm7uFgUOwgQY0S7Lc",
    "ADIDAS": "https://discordapp.com/api/webhooks/1531391310936801443/pPY-QFN2vJyqUjCGtmPvGIQSUXnI7YTbAors1lv3VO1q1-W5BRf4JAKrjgEC4gxbgvh4",
    "TOMMY HILFIGER": "https://discordapp.com/api/webhooks/1531391310936801443/pPY-QFN2vJyqUjCGtmPvGIQSUXnI7YTbAors1lv3VO1q1-W5BRf4JAKrjgEC4gxbgvh4"
}

SEARCHES = [
    {"name": "RALPH LAUREN", "query": "ralph lauren"},
    {"name": "LACOSTE", "query": "lacoste"},
    {"name": "THE NORTH FACE", "query": "the north face"},
    {"name": "IPHONE", "query": "iphone"},
    {"name": "LEGO", "query": "lego"},
    {"name": "NIKE", "query": "nike"},
    {"name": "ADIDAS", "query": "adidas"},
    {"name": "TOMMY HILFIGER", "query": "tommy hilfiger"}
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "hu-HU,hu;q=0.9",
    "Referer": "https://www.vinted.hu/"
}

def run_bot():
    print("Stílusos Vinted sniper bot elindult...")
    seen_items = {item["name"]: set() for item in SEARCHES}

    session = requests.Session()
    session.headers.update(headers)
    
    try:
        session.get("https://www.vinted.hu/", timeout=10)
    except:
        pass

    for target in SEARCHES:
        name = target["name"]
        query = target["query"]
        url = f"https://www.vinted.hu/api/v2/catalog/items?search_text={query}&order=newest_first&per_page=20"
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                for item in response.json().get("items", []):
                    seen_items[name].add(str(item["id"]))
        except:
            pass

    print("Élő figyelés aktív...")

    while True:
        for target in SEARCHES:
            name = target["name"]
            query = target["query"]
            webhook_url = WEBHOOKS[name]
            
            url = f"https://www.vinted.hu/api/v2/catalog/items?search_text={query}&order=newest_first&per_page=5"
            
            try:
                response = session.get(url, timeout=10)
                if response.status_code != 200:
                    continue
                    
                items = response.json().get("items", [])
                
                new_found = []
                for item in items:
                    item_id = str(item["id"])
                    if item_id not in seen_items[name]:
                        seen_items[name].add(item_id)
                        new_found.append(item)
                
                for item in reversed(new_found):
                    title = item.get("title", "Ismeretlen termék")
                    
                    price_data = item.get("price")
                    if isinstance(price_data, dict):
                        amount = price_data.get("amount", "")
                        currency_code = price_data.get("currency_code", "HUF")
                        price = f"{amount} {currency_code}"
                    else:
                        currency = item.get("currency", "HUF")
                        price = f"{price_data} {currency}" if price_data else "Egyeztetés alatt"

                    item_url = item.get("url")
                    
                    photos = item.get("photos", [])
                    photo_url = ""
                    if photos:
                        first_photo = photos[0]
                        if isinstance(first_photo, dict):
                            photo_url = first_photo.get("full_size_url") or first_photo.get("url", "")
                    
                    user = item.get("user", {})
                    username = user.get("login", "Ismeretlen eladó") if isinstance(user, dict) else "Ismeretlen eladó"

                    payload = {
                        "embeds": [{
                            "title": f"🔥 ÚJ {name} AJÁNLAT!",
                            "url": item_url,
                            "color": 5814783,
                            "description": f"**[{title}]({item_url})**",
                            "fields": [
                                {"name": "💰 Ár", "value": f"`{price}`", "inline": True},
                                {"name": "👤 Eladó", "value": f"`{username}`", "inline": True},
                                {"name": "🔗 Gyors Link", "value": f"[Kattints ide a megtekintéshez és vásárláshoz]({item_url})", "inline": False}
                            ],
                            "image": {"url": photo_url} if photo_url else {},
                            "footer": {
                                "text": "Vinted Sniper Bot • Friss hirdetés"
                            }
                        }]
                    }
                    
                    requests.post(webhook_url, json=payload)
                    print(f"Stílusosan kiküldve [{name}]: {title} ({price})")
                    
            except Exception as e:
                pass
                
        time.sleep(5)

if __name__ == "__main__":
    run_bot()

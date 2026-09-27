import os
import json
import datetime
import requests

# --- تنظیمات (از GitHub Secrets خونده می‌شه، نیازی به دست‌زدن نیست) ---
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIPS_PATH = os.path.join(BASE_DIR, "tips.json")
PHOTOS_DIR = os.path.join(BASE_DIR, "photos")

def load_tips():
    with open(TIPS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_today_tip(tips):
    # بر اساس تاریخ امروز، یکی از نکته‌ها رو به صورت چرخشی انتخاب می‌کنه
    # (وقتی نکته‌های بیشتری اضافه کنی، به‌طور خودکار وارد چرخه می‌شن)
    day_index = datetime.date.today().toordinal() % len(tips)
    return tips[day_index]

def find_photo(tip_id):
    for ext in ["jpg", "jpeg", "png"]:
        path = os.path.join(PHOTOS_DIR, f"{tip_id}.{ext}")
        if os.path.exists(path):
            return path
    return None

def send_to_telegram(tip):
    caption = f"🚗 نکته امروز: {tip['title']}\n\n{tip['text']}"
    photo_path = find_photo(tip["id"])

    if photo_path:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(photo_path, "rb") as photo_file:
            resp = requests.post(
                url,
                data={"chat_id": CHANNEL_ID, "caption": caption},
                files={"photo": photo_file},
            )
    else:
        # اگه عکس اون نکته هنوز آپلود نشده باشه، فقط متن ارسال می‌شه
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        resp = requests.post(url, data={"chat_id": CHANNEL_ID, "text": caption})

    resp.raise_for_status()
    print("پیام با موفقیت ارسال شد:", tip["title"])

if __name__ == "__main__":
    all_tips = load_tips()
    today_tip = pick_today_tip(all_tips)
    send_to_telegram(today_tip)

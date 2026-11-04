import os
import json
import random
import time
import textwrap
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")
MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL")
BRIDGE_PAGE_URL = os.environ.get("BRIDGE_PAGE_URL")
REPO_FULL_NAME = os.environ.get("REPO_FULL_NAME", "")

BILLIONAIRES = [
    "Elon Musk", "Sam Altman", "Jensen Huang", "Jeff Bezos", 
    "Bill Gates", "Mark Zuckerberg", "Peter Thiel", "Larry Ellison",
    "Ray Kurzweil", "Naval Ravikant"
]

TOPICS = [
    "Humanoid Robots replacing workers",
    "Brain chips & Neuralink super-intelligence",
    "The collapse of conventional college degrees",
    "AI taking white-collar jobs by 2028",
    "Mars colonization and space economy",
    "Longevity tech & living to 150 years",
    "The end of smartphones and rise of smart glasses",
    "Cryptocurrency & decentralized future economy"
]

COLOR_THEMES = [
    {"accent": (0, 229, 255), "author": (255, 214, 0)},     # Cyan & Gold
    {"accent": (255, 0, 128), "author": (0, 255, 200)},     # Neon Pink & Mint
    {"accent": (0, 255, 136), "author": (255, 255, 255)},   # Neon Green & White
    {"accent": (255, 106, 0), "author": (255, 214, 0)},     # Fiery Orange & Yellow
    {"accent": (168, 85, 247), "author": (56, 189, 248)}    # Purple & Sky Blue
]

def generate_billionaire_content():
    client = genai.Client(api_key=GEMINI_API_KEY)
    chosen_person = random.choice(BILLIONAIRES)
    chosen_topic = random.choice(TOPICS)
    
    prompt = f"""
    Write a bold, provocative, and highly viral prediction by {chosen_person} about: "{chosen_topic}".
    Ensure it is totally fresh, non-cliche, dramatic, and sounds like real tech insider news.
    
    Return strictly JSON with NO formatting backticks:
    {{
      "billionaire": "{chosen_person}",
      "quote_text": "Shocking, punchy prediction in ALL CAPS (10 to 16 words max)",
      "pin_title": "High CTR clickbait title (under 75 chars)",
      "pin_description": "SEO Pinterest description ending with 6 popular hashtags",
      "search_tag": "A single English keyword for image search like cyber, space, server, brain, robot, finance"
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Gemini generation error: {e}")
        return None

def fetch_background_image(search_tag="futuristic"):
    queries = [search_tag, "futuristic dark", "cyberpunk technology", "deep space galaxy", "neon artificial intelligence"]
    q = random.choice(queries)
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={q}&image_type=photo&orientation=vertical&per_page=30"
    
    try:
        res = requests.get(url, timeout=12).json()
        hits = res.get("hits", [])
        if hits:
            img_url = random.choice(hits)["largeImageURL"]
            img_res = requests.get(img_url, timeout=12)
            return Image.open(BytesIO(img_res.content)).convert("RGB")
    except Exception as e:
        print(f"Pixabay fetch error: {e}")
        
    return Image.new("RGB", (1000, 1500), color=(12, 14, 22))

def create_pin_image(data, filename="pin_temp.png"):
    tag = data.get("search_tag", "technology")
    bg = fetch_background_image(tag)
    bg = bg.resize((1000, 1500), Image.Resampling.LANCZOS)
    
    # Random brightness so backgrounds look distinct
    brightness = random.uniform(0.25, 0.35)
    bg = ImageEnhance.Brightness(bg).enhance(brightness)
    
    draw = ImageDraw.Draw(bg)
    theme = random.choice(COLOR_THEMES)
    
    # Dynamic Border Box
    draw.rectangle([45, 45, 955, 1455], outline=theme["accent"], width=3)
    
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        tag_font = ImageFont.truetype(font_path, 32)
        quote_font = ImageFont.truetype(font_path, 54)
        author_font = ImageFont.truetype(font_path, 40)
        cta_font = ImageFont.truetype(font_path, 30)
    except:
        tag_font = quote_font = author_font = cta_font = ImageFont.load_default()

    # Top Tag
    category_tags = ["2030 PREDICTION", "FUTURE TECH BRIEF", "BILLIONAIRE WARNING", "CONFIDENTIAL INSIGHT"]
    draw.text((500, 150), random.choice(category_tags), fill=theme["accent"], font=tag_font, anchor="mm")
    
    # Wrapped Quote
    lines = textwrap.wrap(f'"{data["quote_text"]}"', width=20)
    y_text = 480
    for line in lines:
        draw.text((500, y_text), line, fill=(255, 255, 255), font=quote_font, anchor="mm")
        y_text += 78
        
    # Author
    draw.text((500, y_text + 65), f"— {data['billionaire'].upper()}", fill=theme["author"], font=author_font, anchor="mm")
    
    # CTA Button
    btn_color = theme["accent"]
    draw.rounded_rectangle([200, 1270, 800, 1365], radius=22, fill=btn_color)
    draw.text((500, 1317), "READ FULL REPORT  ➔", fill=(10, 10, 15), font=cta_font, anchor="mm")
    
    bg.save(filename, "PNG", optimize=True)

if __name__ == "__main__":
    # Har run par 5 unique posts banayega
    BATCH_COUNT = 5
    generated_items = []
    
    for i in range(BATCH_COUNT):
        print(f"Generating post {i+1} of {BATCH_COUNT}...")
        item = generate_billionaire_content()
        if item:
            filename = f"pin_{i}.png"
            create_pin_image(item, filename)
            item["local_file"] = filename
            generated_items.append(item)
        time.sleep(2)
        
    with open("batch_payload.json", "w") as f:
        json.dump(generated_items, f)
    print("Batch generation complete!")

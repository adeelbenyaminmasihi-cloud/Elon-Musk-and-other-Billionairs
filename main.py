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

BILLIONAIRES = [
    "Elon Musk", "Sam Altman", "Jensen Huang", "Jeff Bezos", 
    "Bill Gates", "Mark Zuckerberg", "Peter Thiel", "Larry Ellison",
    "Warren Buffett", "Sundar Pichai", "Satya Nadella", "Ray Kurzweil"
]

TOPICS = [
    "Humanoid AI Robots taking physical jobs",
    "Brain computer chips and digital immortality",
    "Why traditional degrees and schooling will collapse",
    "Artificial General Intelligence arriving before 2029",
    "Mars colony, space mining and next trillionaires",
    "Longevity biotechnology to live past 130 years",
    "Smart AI glasses replacing mobile phones completely",
    "The complete restructuring of the global financial system",
    "Autonomous humanoid labor building future mega-cities"
]

COLOR_THEMES = [
    {"accent": (0, 229, 255), "author": (255, 214, 0)},     # Cyan & Gold
    {"accent": (255, 0, 128), "author": (0, 255, 200)},     # Neon Pink & Mint
    {"accent": (0, 255, 136), "author": (255, 255, 255)},   # Neon Green & White
    {"accent": (255, 106, 0), "author": (255, 214, 0)},     # Orange & Yellow
    {"accent": (168, 85, 247), "author": (56, 189, 248)}    # Purple & Cyan
]

TAGS = ["FUTURE PREDICTION", "TECH INSIGHT 2030", "BILLIONAIRE WARNING", "CONFIDENTIAL BRIEF"]

def get_fallback_data(chosen_person, chosen_topic):
    fallbacks = {
        "Jensen Huang": ("EVERY WORKFORCE WILL BE REPLACED BY DIGITAL AI AGENTS.", "Jensen Huang's Warning on the Future of Jobs"),
        "Sam Altman": ("AGI WILL SOLVE THE LAWS OF PHYSICS BEFORE 2030.", "Sam Altman Predicts AGI Breakthrough"),
        "Jeff Bezos": ("TRILLIONS OF HUMANS WILL LIVE IN ORBITING SPACE COLONIES.", "Jeff Bezos Outlines Future Space Civilization"),
        "Bill Gates": ("GLOBAL HEALTH AND AI WILL REDEFINE HUMAN WEALTH.", "Bill Gates Predicts The Next Global Shift"),
        "Mark Zuckerberg": ("THE PHYSICAL WORLD AND DIGITAL METAVERSE WILL MERGE.", "Mark Zuckerberg on the Next Computing Platform"),
        "Peter Thiel": ("COMPETITION IS FOR LOSERS; BUILD A FUTURE MONOPOLY.", "Peter Thiel's Bold Business Blueprint"),
        "Elon Musk": ("BY 2030, OPTIMUS ROBOTS WILL OUTNUMBER THE HUMAN POPULATION.", "Elon Musk Predicts Robotics Takeover")
    }
    quote, title = fallbacks.get(chosen_person, ("THE FUTURE BELONGS TO THOSE WHO OWN THE ALGORITHMS.", f"{chosen_person}'s Shocking Future Prediction"))
    return {
        "billionaire": chosen_person,
        "quote_text": quote,
        "pin_title": title,
        "pin_description": f"{chosen_person} reveals his perspective on {chosen_topic}. Read the full analysis. #Billionaire #FutureTech #AI #Wealth #Innovation",
        "search_tag": "technology dark"
    }

def generate_billionaire_content():
    chosen_person = random.choice(BILLIONAIRES)
    chosen_topic = random.choice(TOPICS)
    
    prompt = f"""
    Write a provocative, completely unique future prediction by {chosen_person} regarding: "{chosen_topic}".
    Return STRICTLY JSON format with no markdown blocks:
    {{
      "billionaire": "{chosen_person}",
      "quote_text": "Dramatic prediction in ALL CAPS (10 to 15 words max)",
      "pin_title": "High CTR clickbait title (under 75 characters)",
      "pin_description": "Engaging Pinterest description with 5 trending hashtags",
      "search_tag": "Single search keyword like robot, space, cyber, brain, neon, tech"
    }}
    """
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        clean = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(clean)
        if not data.get("quote_text") or not data.get("billionaire"):
            return get_fallback_data(chosen_person, chosen_topic)
        return data
    except Exception as e:
        print(f"Gemini API fallback triggered: {e}")
        return get_fallback_data(chosen_person, chosen_topic)

def fetch_background_image(search_tag="technology"):
    queries = [search_tag, "cyberpunk", "futuristic tech", "dark galaxy space", "artificial intelligence neon"]
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
        
    return Image.new("RGB", (1000, 1500), color=(14, 16, 26))

def create_pin_image(data, filename):
    tag = data.get("search_tag", "technology")
    bg = fetch_background_image(tag)
    bg = bg.resize((1000, 1500), Image.Resampling.LANCZOS)
    
    # Har pin ke liye distinct brightness
    bg = ImageEnhance.Brightness(bg).enhance(random.uniform(0.24, 0.34))
    draw = ImageDraw.Draw(bg)
    theme = random.choice(COLOR_THEMES)
    
    # Border
    draw.rectangle([45, 45, 955, 1455], outline=theme["accent"], width=3)
    
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        tag_font = ImageFont.truetype(font_path, 32)
        quote_font = ImageFont.truetype(font_path, 54)
        author_font = ImageFont.truetype(font_path, 40)
        cta_font = ImageFont.truetype(font_path, 30)
    except:
        tag_font = quote_font = author_font = cta_font = ImageFont.load_default()

    # Header Tag
    draw.text((500, 150), random.choice(TAGS), fill=theme["accent"], font=tag_font, anchor="mm")
    
    # Wrapped Quote
    lines = textwrap.wrap(f'"{data["quote_text"]}"', width=20)
    y_text = 480
    for line in lines:
        draw.text((500, y_text), line, fill=(255, 255, 255), font=quote_font, anchor="mm")
        y_text += 78
        
    # Author Name
    draw.text((500, y_text + 65), f"— {data['billionaire'].upper()}", fill=theme["author"], font=author_font, anchor="mm")
    
    # Bottom CTA
    draw.rounded_rectangle([200, 1270, 800, 1365], radius=22, fill=theme["accent"])
    draw.text((500, 1317), "READ FULL REPORT  ➔", fill=(10, 10, 15), font=cta_font, anchor="mm")
    
    bg.save(filename, "PNG", optimize=True)

if __name__ == "__main__":
    # Har run mein 2 distinct posts banengi
    BATCH_COUNT = 2
    batch = []
    
    used_billionaires = set()
    for i in range(BATCH_COUNT):
        item = generate_billionaire_content()
        # Same run mein do same billionaires na hon
        while item["billionaire"] in used_billionaires:
            item = generate_billionaire_content()
        used_billionaires.add(item["billionaire"])
        
        filename = f"pin_{i}.png"
        create_pin_image(item, filename)
        item["local_file"] = filename
        batch.append(item)
        time.sleep(2)
        
    with open("batch_payload.json", "w") as f:
        json.dump(batch, f)
    print("Batch created successfully!")

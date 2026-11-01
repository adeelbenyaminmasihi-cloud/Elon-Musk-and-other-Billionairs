import os
import json
import random
import textwrap
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from google import genai

# Environment Secrets
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")
MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL")
BRIDGE_PAGE_URL = os.environ.get("BRIDGE_PAGE_URL") # e.g. https://username.github.io/repo-name/

def generate_billionaire_content():
    """Gemini API se billionaire quote, title aur SEO description generate karwana"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    billionaires = [
        "Elon Musk", "Sam Altman", "Jeff Bezos", "Jensen Huang", 
        "Bill Gates", "Mark Zuckerberg", "Naval Ravikant", "Peter Thiel"
    ]
    chosen = random.choice(billionaires)
    
    prompt = f"""
    Generate a viral Pinterest post about {chosen}'s bold prediction or warning about the future (AI, Mars, Neuralink, Robotics, Future Economy, or 2030).
    Return strictly valid JSON with NO markdown formatting or backticks, containing these exact keys:
    "billionaire": "{chosen}",
    "quote_text": "A shocking, dramatic 12-18 word quote or prediction about the future in ALL CAPS",
    "pin_title": "Clickbait viral Pinterest title (max 85 characters)",
    "pin_description": "Engaging SEO description explaining the prediction with 5 trending hashtags like #ElonMusk #FutureTech #AI"
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw_text)
    except Exception as e:
        print(f"Gemini error, using fallback: {e}")
        return {
            "billionaire": "Elon Musk",
            "quote_text": "BY 2030, AI WILL BE SMARTER THAN ALL HUMANS COMBINED.",
            "pin_title": "Elon Musk's Shocking 2030 Warning About AI & Humanity",
            "pin_description": "Discover what tech billionaires are saying about the next decade of artificial intelligence and human evolution. #ElonMusk #FutureTech #AI #BillionaireMindset #TechNews"
        }

def fetch_background_image():
    """Pixabay se futuristic / dark tech vertical image uthana"""
    queries = ["artificial intelligence", "cyberpunk city", "space galaxy", "futuristic technology", "robotics dark"]
    q = random.choice(queries)
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={q}&image_type=photo&orientation=vertical&per_page=20"
    
    try:
        res = requests.get(url, timeout=15).json()
        hits = res.get("hits", [])
        if hits:
            img_url = random.choice(hits)["largeImageURL"]
            img_res = requests.get(img_url, timeout=15)
            return Image.open(BytesIO(img_res.content)).convert("RGB")
    except Exception as e:
        print(f"Pixabay error: {e}")
    
    # Fallback dark canvas agar internet/API fail ho
    return Image.new("RGB", (1000, 1500), color=(15, 18, 28))

def create_pin_image(data, output_path="latest_pin.png"):
    """1000x1500 professional Pinterest graphic banana"""
    bg = fetch_background_image()
    bg = bg.resize((1000, 1500), Image.Resampling.LANCZOS)
    
    # Image ko dark karna taake text saaf nazar aaye
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.32)
    
    draw = ImageDraw.Draw(bg)
    
    # Border Frame Draw Karna
    draw.rectangle([45, 45, 955, 1455], outline=(0, 210, 255), width=3)
    
    # Fonts load karna (Ubuntu GitHub runner par DejaVuSans-Bold mojood hota hai)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        tag_font = ImageFont.truetype(font_path, 34)
        quote_font = ImageFont.truetype(font_path, 58)
        author_font = ImageFont.truetype(font_path, 42)
        cta_font = ImageFont.truetype(font_path, 30)
    except:
        tag_font = quote_font = author_font = cta_font = ImageFont.load_default()

    # Top Category Tag
    draw.text((500, 140), "FUTURE PREDICTION", fill=(0, 210, 255), font=tag_font, anchor="mm")
    
    # Center Quote Text (Word Wrap)
    lines = textwrap.wrap(f'"{data["quote_text"]}"', width=20)
    y_text = 460
    for line in lines:
        draw.text((500, y_text), line, fill=(255, 255, 255), font=quote_font, anchor="mm")
        y_text += 82
        
    # Billionaire Name
    draw.text((500, y_text + 60), f"— {data['billionaire'].upper()}", fill=(255, 204, 0), font=author_font, anchor="mm")
    
    # Bottom Call-To-Action Button
    draw.rounded_rectangle([200, 1270, 800, 1365], radius=20, fill=(0, 210, 255))
    draw.text((500, 1317), "READ FULL PREDICTION  ➔", fill=(10, 10, 20), font=cta_font, anchor="mm")
    
    bg.save(output_path, "PNG", optimize=True)
    print("Pin Image Generated Successfully!")

if __name__ == "__main__":
    content = generate_billionaire_content()
    create_pin_image(content, "latest_pin.png")
    
    # Content metadata ko file mein save karna taake Git push ke baad webhook ko bhej sakein
    with open("payload.json", "w") as f:
        json.dump(content, f)

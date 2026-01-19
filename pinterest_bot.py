import os
import re
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIG ==========
BOT_TOKEN = "8471774303:AAFZeoEsxbgt8OR7CvZgdy0z2xKE_m52H-I"  # BotFather se milega
SAVE_PATH = "/sdcard/Download/Pinterest_Bot"
HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 12; Mobile)"}
PINIMG_REGEX = r"https://i\.pinimg\.com/originals/[a-z0-9/]+\.(jpg|jpeg|png|webp)"

# ========== FUNCTIONS ==========
def ensure_folder():
    os.makedirs(SAVE_PATH, exist_ok=True)

def extract_images(pin_url):
    """Pinterest page se original images extract karo"""
    resp = requests.get(pin_url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        raise Exception("Pinterest page load nahi hua")
    
    html = resp.text
    final_urls = []
    for match in re.finditer(PINIMG_REGEX, html):
        final_urls.append(match.group(0))
    
    return list(set(final_urls))

def download_image(img_url):
    """Single image download karo aur path return karo"""
    name = img_url.split("/")[-1]
    path = os.path.join(SAVE_PATH, name)
    
    r = requests.get(img_url, headers=HEADERS, stream=True, timeout=20)
    if r.status_code == 200:
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return path
    return None

# ========== BOT HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    welcome_msg = (
        "📌 *Pinterest Original Image Downloader Bot*\n\n"
        "🖼 High Quality Images Download\n"
        "🎯 Original Quality (No Watermark)\n\n"
        "📝 *Kaise Use Kare:*\n"
        "1️⃣ Pinterest se koi pin ka link copy karo\n"
        "2️⃣ Mujhe send karo\n"
        "3️⃣ Main tumhe original images bhej dunga!\n\n"
        "💡 Example:\n"
        "`https://pin.it/xxxxx`\n"
        "`https://www.pinterest.com/pin/xxxxx`\n\n"
        "Made by @ninjaxz_07"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pinterest links handle karo"""
    user_msg = update.message.text.strip()
    
    # Check if Pinterest link hai
    if not ("pinterest.com" in user_msg or "pin.it" in user_msg):
        await update.message.reply_text(
            "❌ Please send a valid Pinterest link!\n\n"
            "Example:\n"
            "https://pin.it/xxxxx\n"
            "https://www.pinterest.com/pin/xxxxx"
        )
        return
    
    # Processing message
    status_msg = await update.message.reply_text("🔍 Searching for original images...")
    
    try:
        # Extract images
        urls = extract_images(user_msg)
        
        if not urls:
            await status_msg.edit_text("❌ No original images found on this pin!")
            return
        
        await status_msg.edit_text(f"✅ Found {len(urls)} image(s)!\n📥 Downloading...")
        
        # Download aur send karo
        ensure_folder()
        sent_count = 0
        
        for i, img_url in enumerate(urls, 1):
            try:
                # Download
                file_path = download_image(img_url)
                
                if file_path and os.path.exists(file_path):
                    # Telegram pe send karo
                    with open(file_path, 'rb') as photo:
                        await update.message.reply_photo(
                            photo=photo,
                            caption=f"📌 Image {i}/{len(urls)}\n🔗 Original Quality"
                        )
                    sent_count += 1
                    
                    # File delete karo (optional - space bachane ke liye)
                    # os.remove(file_path)
                    
            except Exception as e:
                print(f"Error sending image {i}: {e}")
                continue
        
        # Final status
        if sent_count > 0:
            await status_msg.edit_text(
                f"✅ *Download Complete!*\n\n"
                f"📊 Sent: {sent_count}/{len(urls)} images\n"
                f"📂 Also saved in: {SAVE_PATH}",
                parse_mode='Markdown'
            )
        else:
            await status_msg.edit_text("❌ Failed to download images. Please try again!")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}\n\nPlease check the link and try again!")

# ========== MAIN ==========
def main():
    """Bot start karo"""
    print("🤖 Bot starting...")
    
    # Application create karo
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers add karo
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    # Bot run karo
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    ensure_folder()
    main()

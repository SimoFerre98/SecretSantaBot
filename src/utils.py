import json
import os
import uuid

# Ottieni la directory base del progetto (una cartella sopra 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_data(filename):
    # Se il filename non è assoluto, lo rendiamo relativo a BASE_DIR
    if not os.path.isabs(filename):
        filepath = os.path.join(BASE_DIR, filename)
    else:
        filepath = filename
        
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(filename, data):
    # Se il filename non è assoluto, lo rendiamo relativo a BASE_DIR
    if not os.path.isabs(filename):
        filepath = os.path.join(BASE_DIR, filename)
    else:
        filepath = filename

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def generate_unique_id():
    return str(uuid.uuid4())

def get_main_menu_keyboard():
    """Crea una tastiera Inline per il menu principale."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
    keyboard = [
        [
            InlineKeyboardButton("🎅 Apri Mini App", web_app=WebAppInfo(url="https://sferrero.github.io/SecretSantaBot/webapp/index.html")), # Placeholder URL
        ],
        [
            InlineKeyboardButton("👥 Partecipanti", callback_data="participants"),
            InlineKeyboardButton("🎁 Wishlist", callback_data="wishlist"),
        ],
        [
            InlineKeyboardButton("🚫 Esclusioni", callback_data="exclusions"),
            InlineKeyboardButton("🎲 Shuffle", callback_data="shuffle"),
        ],
        [
            InlineKeyboardButton("🔙 Esci dal Gruppo", callback_data="leave_group")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_response(update, message: str):
    """Invia una risposta in base al contesto (message o callback_query)."""
    if update.message:
        await update.message.reply_text(message)
    elif update.callback_query:
        await update.callback_query.answer(message)


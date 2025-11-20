import json
import os
import uuid

def load_data(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def generate_unique_id():
    return str(uuid.uuid4())

def get_group_keyboard():
    """Crea una tastiera per interagire con il gruppo."""
    from telegram import KeyboardButton, ReplyKeyboardMarkup
    keyboard = [
        [KeyboardButton("Partecipanti"), KeyboardButton("Aggiungi Wishlist")],
        [KeyboardButton("Esclusioni"), KeyboardButton("Shuffle")],
        [KeyboardButton("Torna al Menu Gruppi")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def send_response(update, message: str):
    """Invia una risposta in base al contesto (message o callback_query)."""
    if update.message:
        await update.message.reply_text(message)
    elif update.callback_query:
        await update.callback_query.answer(message)


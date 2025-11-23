import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = "7548642306:AAFIFgN95ntOFGdcI2-sHS7T3y3zCCut4R8"
CHAT_ID = 139657524  # Simo

async def send_demo_ui():
    bot = Bot(token=BOT_TOKEN)
    
    # Esempio di Inline Keyboard (Grafica Migliorata)
    keyboard = [
        [
            InlineKeyboardButton("🎁 La mia Wishlist", callback_data="wishlist"),
            InlineKeyboardButton("👥 Partecipanti", callback_data="participants"),
        ],
        [
            InlineKeyboardButton("🚫 Esclusioni", callback_data="exclusions"),
            InlineKeyboardButton("🎲 Shuffle", callback_data="shuffle"),
        ],
        [
            InlineKeyboardButton("🔗 Apri Dashboard (Web)", url="https://www.google.com")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "<b>🎅 Secret Santa UI Demo</b>\n\n"
        "Ciao! Questa è una dimostrazione di come potrebbe apparire il bot con una grafica migliorata.\n\n"
        "✅ <b>Pulsanti Inline:</b> Più puliti e integrati nel messaggio.\n"
        "✅ <b>Formattazione HTML:</b> Testo in grassetto, liste, ecc.\n"
        "✅ <b>Link Esterni:</b> Puoi aprire direttamente la dashboard.\n\n"
        "<i>Ti piace questo stile?</i>"
    )
    
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML", reply_markup=reply_markup)
        print("Messaggio demo inviato con successo!")
    except Exception as e:
        print(f"Errore invio demo: {e}")

if __name__ == "__main__":
    asyncio.run(send_demo_ui())

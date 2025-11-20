from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
import json

# Configura il token del bot e la cartella del gruppo
BOT_TOKEN = "7548642306:AAFIFgN95ntOFGdcI2-sHS7T3y3zCCut4R8"
GROUP_FOLDER = "data/5b506af4-2cfe-4486-ba6e-99358923838f"

def load_data(filename):
    """Carica i dati da un file JSON."""
    filepath = os.path.join(GROUP_FOLDER, filename)
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {filename} non trovato.")
        return {}

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inoltra i messaggi dal ricevente al Secret Santa assegnato."""
    participants = load_data("participants.json")
    shuffle_results = load_data("shuffle.json")

    sender_id = update.effective_user.id
    sender_name = None

    # Trova il nome del mittente in base all'ID Telegram
    for name, chat_id in participants.items():
        if chat_id == sender_id:
            sender_name = name
            break

    if not sender_name:
        await update.message.reply_text("Non sei registrato per il Secret Santa!")
        return

    # Trova chi deve fare il regalo
    giver_name = None
    for receiver, giver in shuffle_results.items():
        if receiver == sender_name:
            giver_name = giver
            break

    if not giver_name:
        await update.message.reply_text("Non riesco a trovare il tuo Secret Santa. Contatta l'organizzatore.")
        return

    giver_id = participants.get(giver_name)
    if not giver_id:
        await update.message.reply_text("Non riesco a trovare il tuo Secret Santa. Contatta l'organizzatore.")
        return

    # Inoltra il messaggio al Secret Santa
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(
            chat_id=giver_id,
            text=f"{update.message.text}"
        )
        await update.message.reply_text("Messaggio inviato al tuo Secret Santa!")
    except Exception as e:
        print(f"Errore nell'invio del messaggio al Secret Santa (ID: {giver_id}): {e}")
        await update.message.reply_text("Errore nell'invio del messaggio. Riprova più tardi.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /start."""
    await update.message.reply_text(
        "Ciao! Benvenuto al Secret Santa! Inviami un messaggio e lo inoltrerò al tuo Secret Santa."
    )

def main():
    """Avvia il bot."""
    # Configura l'applicazione del bot
    app = Application.builder().token(BOT_TOKEN).build()

    # Comandi
    app.add_handler(CommandHandler("start", start))

    # Gestore per inoltrare messaggi
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    print("Il bot è in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()

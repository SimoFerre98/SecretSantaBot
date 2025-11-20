from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Token del bot
bot_token = "7548642306:AAFIFgN95ntOFGdcI2-sHS7T3y3zCCut4R8"

# Dizionario per memorizzare i partecipanti
participants = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce il comando /start e registra i partecipanti."""
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name

    if user_name not in participants:
        participants[user_name] = chat_id
        await update.message.reply_text(f"Ciao {user_name}! Sei stato registrato per il Secret Santa 🎅")
        print(f"Partecipante registrato: {user_name}, Chat ID: {chat_id}")
    else:
        await update.message.reply_text(f"Sei già registrato, {user_name}!")

async def show_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra i partecipanti registrati (solo per debug)."""
    if participants:
        participant_list = "\n".join(participants.keys())
        await update.message.reply_text(f"Partecipanti:\n{participant_list}")
    else:
        await update.message.reply_text("Nessun partecipante registrato al momento.")

def main():
    """Avvia l'applicazione Telegram."""
    application = Application.builder().token(bot_token).build()

    # Aggiunge i gestori per i comandi
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("participants", show_participants))

    print("Il bot è in esecuzione...")
    application.run_polling()

if __name__ == "__main__":
    main()

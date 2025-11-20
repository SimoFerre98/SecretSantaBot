from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from group_management import create_group, join_group
from group_actions import show_participants
from utils import get_group_keyboard, load_data
import os

SETTINGS_FILE = "settings.json"

def is_bot_active():
    if os.path.exists(SETTINGS_FILE):
        settings = load_data(SETTINGS_FILE)
        return settings.get("bot_active", True)
    return True

async def check_maintenance(update: Update):
    if not is_bot_active():
        await update.message.reply_text("⚠️ Il bot è attualmente in manutenzione. Riprova più tardi.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Messaggio di benvenuto."""
    if not await check_maintenance(update): return
    await update.message.reply_text("Benvenuto! Usa il menu comandi per interagire con il bot.")

async def creategroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea un nuovo gruppo e lo imposta come attivo."""
    if not await check_maintenance(update): return
    
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    group_id = create_group(user_name, chat_id)

    # Memorizza il nuovo gruppo come attivo
    context.user_data["current_group"] = group_id

    await update.message.reply_text(
        f"✅ Gruppo creato con successo! ID del gruppo: {group_id}\nSeleziona un'azione dal menu:",
        reply_markup=get_group_keyboard()
    )

async def joingroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aggiungi l'utente a un gruppo e imposta il gruppo attivo."""
    if not await check_maintenance(update): return
    
    if not context.args:
        await update.message.reply_text("Usa il comando /joingroup <ID del gruppo> per accedere a un gruppo.")
        return

    group_id = context.args[0]
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    success, message = join_group(group_id, user_name, chat_id)

    if success:
        # Memorizza il gruppo attivo per l'utente
        context.user_data["current_group"] = group_id
        await update.message.reply_text(
            f"✅ {message}\nSeleziona un'azione dal menu:",
            reply_markup=get_group_keyboard()
        )
    else:
        await update.message.reply_text(f"❌ {message}")

async def participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra i partecipanti del gruppo attivo."""
    if not await check_maintenance(update): return
    
    # Recupera il gruppo attivo dall'utente
    group_id = context.user_data.get("current_group")
    if not group_id:
        response = "Devi prima accedere a un gruppo."
    else:
        participant_list = show_participants(group_id)
        response = f"Partecipanti del gruppo:\n{participant_list}"

    # Controlla il contesto e invia la risposta nel modo appropriato
    if update.message:
        await update.message.reply_text(response)
    elif update.callback_query:
        await update.callback_query.answer(response)


    participant_list = show_participants(group_id)
    await update.message.reply_text(f"Partecipanti del gruppo:\n{participant_list}")

async def back_to_group_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Torna al menu dei gruppi."""
    if not await check_maintenance(update): return
    
    context.user_data.pop("current_group", None)  # Rimuove il gruppo attivo
    await update.message.reply_text(
        "Sei tornato al menu dei gruppi. Usa i comandi per selezionare o creare un nuovo gruppo.",
        reply_markup=None
    )

def main():
    app = Application.builder().token("7548642306:AAFIFgN95ntOFGdcI2-sHS7T3y3zCCut4R8").build()

    # Comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("creategroup", creategroup))
    app.add_handler(CommandHandler("joingroup", joingroup))
    app.add_handler(CommandHandler("participants", participants))
    app.add_handler(CommandHandler("back", back_to_group_menu))

    print("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()

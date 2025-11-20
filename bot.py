from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from group_management import create_group, join_group
from group_actions import show_participants
from utils import get_group_keyboard
from group_actions import participants

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Messaggio di benvenuto."""
    await update.message.reply_text("Benvenuto! Usa il menu comandi per interagire con il bot.")

async def creategroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea un nuovo gruppo e lo imposta come attivo."""
    user_name = update.effective_user.first_name
    group_id = create_group(user_name)

    # Memorizza il nuovo gruppo come attivo
    context.user_data["current_group"] = group_id

    await update.message.reply_text(
        f"✅ Gruppo creato con successo! ID del gruppo: {group_id}\nSeleziona un'azione dal menu:",
        reply_markup=get_group_keyboard()
    )

async def joingroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aggiungi l'utente a un gruppo e imposta il gruppo attivo."""
    if not context.args:
        await update.message.reply_text("Usa il comando /joingroup <ID del gruppo> per accedere a un gruppo.")
        return

    group_id = context.args[0]
    user_name = update.effective_user.first_name
    success, message = join_group(group_id, user_name)

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

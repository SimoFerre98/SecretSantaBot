from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from group_management import create_group, join_group, get_all_groups, save_wishlist
from group_actions import show_participants
from utils import get_main_menu_keyboard, load_data
import os

SETTINGS_FILE = "settings.json"

# Stati per la conversazione
GROUP_NAME = 0
WAITING_WISHLIST = 1

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
    # Invia un messaggio per rimuovere la vecchia tastiera
    await update.message.reply_text(
        "Benvenuto! Usa il menu comandi per interagire con il bot.",
        reply_markup=ReplyKeyboardRemove()
    )

async def start_create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inizia il processo di creazione del gruppo chiedendo il nome."""
    if not await check_maintenance(update): return ConversationHandler.END
    
    await update.message.reply_text(
        "Inserisci il nome univoco per il nuovo gruppo (es. 'Natale 2025'):\n"
        "Digita /cancel per annullare.",
        reply_markup=ReplyKeyboardRemove()
    )
    return GROUP_NAME

async def receive_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Riceve il nome del gruppo e tenta di crearlo."""
    group_name = update.message.text
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    
    group_id, msg = create_group(user_name, chat_id, group_name)
    
    if not group_id:
        await update.message.reply_text(f"❌ {msg}\nRiprova con un altro nome o /cancel.")
        return GROUP_NAME
    
    # Memorizza il nuovo gruppo come attivo
    context.user_data["current_group"] = group_id

    await update.message.reply_text(
        f"✅ {msg}\nID del gruppo: {group_id}\nSeleziona un'azione dal menu:",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Annulla la conversazione."""
    await update.message.reply_text("Operazione annullata.")
    return ConversationHandler.END

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elenca tutti i gruppi disponibili."""
    if not await check_maintenance(update): return
    
    groups = get_all_groups()
    if groups:
        msg = "📋 **Gruppi Disponibili:**\n" + "\n".join([f"- {g}" for g in groups])
    else:
        msg = "Nessun gruppo trovato."
        
    await update.message.reply_text(msg, parse_mode="Markdown")

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
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await update.message.reply_text(f"❌ {message}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i click sui pulsanti inline."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    group_id = context.user_data.get("current_group")
    
    if not group_id:
        await query.edit_message_text("⚠️ Sessione scaduta. Usa /joingroup per rientrare.")
        return

    if data == "participants":
        participant_list = show_participants(group_id)
        await query.edit_message_text(
            f"👥 **Partecipanti:**\n{participant_list}",
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )
    
    elif data == "leave_group":
        context.user_data.pop("current_group", None)
        await query.edit_message_text("🔙 Sei uscito dal gruppo.")
        return ConversationHandler.END
    
    elif data == "wishlist":
        await query.edit_message_text("🎁 Cosa vorresti ricevere? Scrivilo qui sotto:")
        return WAITING_WISHLIST

    elif data in ["exclusions", "shuffle"]:
        await query.edit_message_text(
            f"🚧 Funzionalità '{data}' in arrivo! Usa la Dashboard per ora.",
            reply_markup=get_main_menu_keyboard()
        )
    return ConversationHandler.END

async def receive_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Riceve e salva la wishlist dell'utente."""
    wish = update.message.text
    user_name = update.effective_user.first_name
    group_id = context.user_data.get("current_group")
    
    if not group_id:
        await update.message.reply_text("⚠️ Errore: Gruppo non trovato. Usa /joingroup.")
        return ConversationHandler.END

    save_wishlist(group_id, user_name, wish)
    
    await update.message.reply_text(
        f"✅ Wishlist salvata: '{wish}'",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END

async def participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra i partecipanti del gruppo attivo."""
    # Manteniamo questo comando per compatibilità ma usiamo la logica inline se possibile
    pass

def main():
    app = Application.builder().token("7548642306:AAFIFgN95ntOFGdcI2-sHS7T3y3zCCut4R8").build()

    # Comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start", start))
    
    # Conversation Handler per la creazione del gruppo
    conv_handler_create = ConversationHandler(
        entry_points=[CommandHandler("creategroup", start_create_group)],
        states={
            GROUP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_group_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler_create)

    # Conversation Handler per la gestione dei bottoni (inclusa Wishlist)
    conv_handler_buttons = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            WAITING_WISHLIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_wishlist)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True
    )
    app.add_handler(conv_handler_buttons)

    print("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()

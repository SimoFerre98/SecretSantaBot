from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from group_management import create_group, join_group, get_all_groups, save_wishlist, approve_join_request
from group_actions import show_participants
from utils import get_main_menu_keyboard, load_data
import os

# Il file settings.json è nella root, quindi dobbiamo salire di un livello
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json")

# Stati per la conversazione
GROUP_NAME, VISIBILITY, ACCESS_CODE = range(3)
WAITING_WISHLIST = 3

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
    """Riceve il nome del gruppo e chiede la visibilità."""
    group_name = update.message.text
    context.user_data["new_group_name"] = group_name
    
    # Chiedi visibilità con tastiera inline
    keyboard = [
        [InlineKeyboardButton("🔓 Pubblico (Tutti possono entrare)", callback_data="public")],
        [InlineKeyboardButton("🔒 Privato (Approvazione Admin)", callback_data="private")]
    ]
    
    await update.message.reply_text(
        f"Hai scelto il nome: {group_name}.\nOra scegli la visibilità:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return VISIBILITY

async def receive_visibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Riceve la visibilità e crea il gruppo."""
    query = update.callback_query
    await query.answer()
    
    visibility = query.data
    context.user_data["visibility"] = visibility
    
    if visibility == "private":
        await query.edit_message_text("🔒 Hai scelto Privato. Inserisci un codice di accesso per il gruppo:")
        return ACCESS_CODE
    
    # Se pubblico, crea direttamente
    return await create_group_flow(update, context)

async def receive_access_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Riceve il codice di accesso e crea il gruppo."""
    access_code = update.message.text
    context.user_data["access_code"] = access_code
    return await create_group_flow(update, context)

async def create_group_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logica finale di creazione gruppo."""
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    
    group_name = context.user_data["new_group_name"]
    visibility = context.user_data["visibility"]
    access_code = context.user_data.get("access_code")
    
    group_id, msg = create_group(user_name, group_name, chat_id, visibility, access_code)

    if not group_id:
        await update.effective_message.reply_text(f"❌ {msg}\nDigita un altro nome o /cancel.")
        return GROUP_NAME
    
    context.user_data["current_group"] = group_id

    await update.effective_message.reply_text(
        f"✅ {msg}\nID del gruppo: {group_id}\nSeleziona un'azione dal menu:",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Annulla la conversazione."""
    await update.message.reply_text("Operazione annullata.")
    return ConversationHandler.END

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elenca tutti i gruppi disponibili con pulsanti."""
    if not await check_maintenance(update): return
    
    groups = load_data(os.path.join(os.path.dirname(SETTINGS_FILE), "groups", "groups.json"))
    
    if not groups:
        await update.message.reply_text("Nessun gruppo trovato.")
        return

    keyboard = []
    for g_id, g in groups.items():
        icon = "🔒" if g.get("visibility") == "private" else "🔓"
        keyboard.append([InlineKeyboardButton(f"{icon} {g['name']}", callback_data=f"view_group_{g_id}")])
    
    await update.message.reply_text("📋 **Seleziona un gruppo per vedere i dettagli:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

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
        # Se è una richiesta pendente (success=False ma messaggio specifico)
        if "richiesta è stata inviata" in message:
             # Notifica l'admin (simulazione, in realtà bisognerebbe trovare l'admin del gruppo)
             # Per semplicità, qui inviamo solo il messaggio all'utente.
             # L'admin dovrebbe ricevere una notifica se avessimo il suo chat_id.
             # Ma group_management non salva il chat_id dell'admin nel dizionario principale, solo in participants.
             # Per ora ci limitiamo a dire all'utente di aspettare.
             await update.message.reply_text(f"⏳ {message}")
             
             # TODO: Implementare notifica all'admin.
             # Per farlo servirebbe caricare participants.json, trovare l'admin e mandargli un messaggio con bottone.
             pass
        else:
            await update.message.reply_text(f"❌ {message}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i click sui pulsanti inline."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Gestione approvazione richieste (formato: approve_GROUPID_USERNAME)
    if data.startswith("approve_"):
        _, group_id, user_to_approve = data.split("_", 2)
        success, user_chat_id = approve_join_request(group_id, user_to_approve)
        
        if success:
            await query.edit_message_text(f"✅ Richiesta di {user_to_approve} approvata!")
        else:
            await query.edit_message_text("❌ Errore nell'approvazione.")
        return

    # Gestione visualizzazione gruppo
    if data.startswith("view_group_"):
        group_id = data.replace("view_group_", "")
        groups = load_data(os.path.join(os.path.dirname(SETTINGS_FILE), "groups", "groups.json"))
        group = groups.get(group_id)
        
        if not group:
            await query.edit_message_text("❌ Gruppo non trovato.")
            return
            
        visibility = group.get("visibility", "public")
        icon = "🔒" if visibility == "private" else "🔓"
        members = ", ".join(group.get("members", []))
        
        msg = (f"**{icon} {group['name']}**\n"
               f"👑 Admin: {group['admin']}\n"
               f"👥 Partecipanti ({len(group['members'])}): {members}\n")
        
        # Bottone per unirsi
        keyboard = [[InlineKeyboardButton("➕ Unisciti al Gruppo", callback_data=f"join_group_btn_{group_id}")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # Gestione unione al gruppo via bottone
    if data.startswith("join_group_btn_"):
        group_id = data.replace("join_group_btn_", "")
        user_name = query.from_user.first_name
        chat_id = query.message.chat_id
        
        success, message = join_group(group_id, user_name, chat_id)
        
        if success:
            context.user_data["current_group"] = group_id
            await query.edit_message_text(
                f"✅ {message}\nSeleziona un'azione dal menu:",
                reply_markup=get_main_menu_keyboard()
            )
        else:
             if "richiesta è stata inviata" in message:
                 await query.edit_message_text(f"⏳ {message}")
             else:
                 await query.edit_message_text(f"❌ {message}")
        return

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
    app.add_handler(CommandHandler("listgroups", list_groups))
    app.add_handler(CommandHandler("joingroup", joingroup))
    
    # Conversation Handler per la creazione del gruppo
    conv_handler_create = ConversationHandler(
        entry_points=[CommandHandler("creategroup", start_create_group)],
        states={
            GROUP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_group_name)],
            VISIBILITY: [CallbackQueryHandler(receive_visibility)],
            ACCESS_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_access_code)],
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

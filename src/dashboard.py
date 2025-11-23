import streamlit as st
import json
import os
import asyncio
import shutil
from telegram import Bot
from group_actions import shuffle_group, manage_exclusions
from send_results import send_results_to_group
from group_management import create_group

# Configurazione
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUPS_FILE = os.path.join(BASE_DIR, "groups", "groups.json")
DATA_DIR = os.path.join(BASE_DIR, "data")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
BOT_TOKEN = "7548642306:AAFIFgN95ntOFGdcI2-sHS7T3y3zCCut4R8" # Idealmente da .env

st.set_page_config(page_title="Secret Santa Dashboard", page_icon="🎅", layout="wide")

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def delete_group(group_id):
    groups = load_json(GROUPS_FILE)
    if group_id not in groups:
        return False, "Gruppo non trovato."
    groups.pop(group_id, None)
    save_json(GROUPS_FILE, groups)
    group_dir = os.path.join(DATA_DIR, group_id)
    if os.path.isdir(group_dir):
        try:
            shutil.rmtree(group_dir)
        except Exception as e:
            return False, f"Errore eliminazione dati del gruppo: {e}"
    return True, "Gruppo eliminato con successo."

async def send_telegram_message(chat_id, text):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        return True, None
    except Exception as e:
        return False, str(e)

st.title("🎅 Secret Santa Bot Dashboard")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Impostazioni")

# 1. Bot Status Toggle
settings = load_json(SETTINGS_FILE)
bot_active = settings.get("bot_active", True)
new_status = st.sidebar.toggle("Bot Attivo", value=bot_active)
if new_status != bot_active:
    settings["bot_active"] = new_status
    save_json(SETTINGS_FILE, settings)
    st.sidebar.success(f"Bot {'attivato' if new_status else 'disattivato'}!")

st.sidebar.divider()

# 2. Group Selection
if os.path.exists(GROUPS_FILE):
    groups = load_json(GROUPS_FILE)
    group_options = {v['name']: k for k, v in groups.items()}
    
    selected_group_name = st.sidebar.selectbox("Seleziona Gruppo", list(group_options.keys()))
    selected_group_id = group_options[selected_group_name] if group_options else None
    
    if selected_group_id:
        st.sidebar.info(f"ID: {selected_group_id}")
        st.sidebar.write(f"**Admin:** {groups[selected_group_id]['admin']}")
else:
    groups = {}
    selected_group_id = None
    st.sidebar.warning("Nessun gruppo trovato.")

st.sidebar.divider()

# 3. Create New Group
with st.sidebar.expander("➕ Crea Nuovo Gruppo"):
    new_group_name = st.text_input("Nome Admin del Gruppo")
    new_group_title = st.text_input("Nome del Gruppo")
    visibility = st.radio("Visibilità", ["public", "private"], format_func=lambda x: "Pubblico 🔓" if x == "public" else "Privato 🔒")
    
    access_code = None
    if visibility == "private":
        access_code = st.text_input("Codice di Accesso", type="password")
    
    if st.button("Crea Gruppo"):
        if new_group_name and new_group_title:
            if visibility == "private" and not access_code:
                st.error("Inserisci un codice di accesso per il gruppo privato.")
            else:
                new_id, msg = create_group(new_group_name, new_group_title, visibility=visibility, access_code=access_code)
                if new_id:
                    st.success(f"Gruppo creato! ID: {new_id}")
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.error("Inserisci un nome.")

if selected_group_id:
    st.sidebar.divider()
    with st.sidebar.expander("🗑️ Elimina Gruppo"):
        confirm_del = st.checkbox("Confermo eliminazione definitiva", key="confirm_del")
        if st.button("Elimina Gruppo", key="btn_del", disabled=not confirm_del):
            ok, msg = delete_group(selected_group_id)
            if ok:
                st.sidebar.success(msg)
                st.rerun()
            else:
                st.sidebar.error(msg)

if not selected_group_id:
    st.stop()

# --- MAIN CONTENT ---

# Carica dati del gruppo selezionato
group_path = os.path.join(DATA_DIR, selected_group_id)
participants_file = os.path.join(group_path, "participants.json")
exclusions_file = os.path.join(group_path, "exclusions.json")
wishlist_file = os.path.join(group_path, "wishlist.json")
shuffle_file = os.path.join(group_path, "shuffle.json")

participants = load_json(participants_file)
exclusions = load_json(exclusions_file)
wishlist = load_json(wishlist_file)
shuffle_results = load_json(shuffle_file)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Partecipanti", "🎁 Wishlist", "🚫 Esclusioni", "⚙️ Gestione Gioco", "💬 Messaggi"])

with tab1:
    st.header("Gestione Partecipanti")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        # Tabella personalizzata con azioni
        for name, chat_id in participants.items():
            c1, c2, c3 = st.columns([3, 2, 2])
            c1.write(f"**{name}**")
            c2.write(f"`{chat_id}`")
            
            is_admin = (groups[selected_group_id]["admin"] == name)
            if is_admin:
                c3.caption("👑 Admin")
            else:
                if c3.button("Promuovi Admin", key=f"prom_{name}"):
                    groups[selected_group_id]["admin"] = name
                    save_json(GROUPS_FILE, groups)
                    st.success(f"{name} è ora l'admin!")
                    st.rerun()

    with col2:
        st.subheader("Aggiungi Partecipante")
        new_name = st.text_input("Nome")
        new_chat_id = st.text_input("Chat ID (opzionale)")
        if st.button("Aggiungi / Aggiorna"):
            if new_name:
                # Se l'utente esiste già, aggiorniamo il Chat ID
                if new_name in participants:
                    st.info(f"Aggiornamento utente esistente: {new_name}")
                
                participants[new_name] = int(new_chat_id) if new_chat_id.isdigit() else "MANUAL_ENTRY"
                save_json(participants_file, participants)
                
                if new_name not in groups[selected_group_id]["members"]:
                    groups[selected_group_id]["members"].append(new_name)
                    save_json(GROUPS_FILE, groups)
                
                st.success(f"{new_name} salvato!")
                st.rerun()
            else:
                st.error("Inserisci un nome.")

        st.subheader("Rimuovi Partecipante")
        to_remove = st.selectbox("Seleziona da rimuovere", list(participants.keys()), key="remove_box")
        if st.button("Rimuovi"):
            if to_remove in participants:
                del participants[to_remove]
                save_json(participants_file, participants)
                
                if to_remove in groups[selected_group_id]["members"]:
                    groups[selected_group_id]["members"].remove(to_remove)
                    save_json(GROUPS_FILE, groups)
                    
                st.success(f"{to_remove} rimosso!")
                st.rerun()

with tab2:
    st.header("Wishlist dei Partecipanti")
    st.table([{"Nome": name, "Desiderio": wish} for name, wish in wishlist.items()])

with tab3:
    st.header("Esclusioni (Chi NON deve regalare a Chi)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Esclusioni Attuali")
        st.json(exclusions)
    
    with col2:
        st.write("### Aggiungi Esclusione")
        giver = st.selectbox("Chi fa il regalo?", list(participants.keys()), key="exc_giver")
        receiver = st.selectbox("Chi NON può riceverlo?", list(participants.keys()), key="exc_receiver")
        
        if st.button("Aggiungi Esclusione"):
            if giver == receiver:
                st.error("Non puoi escludere te stesso (è automatico).")
            else:
                msg = manage_exclusions(selected_group_id, giver, receiver)
                st.success(msg)
                st.rerun()

with tab4:
    st.header("Controlli di Gioco")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Sorteggio")
        if st.button("🔀 Esegui Sorteggio (Shuffle)", type="primary"):
            admin_name = groups[selected_group_id]["admin"]
            result = shuffle_group(selected_group_id, admin_name)
            st.info(result)
            if "completato" in result:
                st.rerun()
        
        if shuffle_results:
            st.success("Sorteggio effettuato!")
            with st.expander("Vedi Risultati (Spoiler!)"):
                st.json(shuffle_results)
        else:
            st.warning("Sorteggio non ancora effettuato.")

    with col2:
        st.subheader("2. Invio Risultati")
        if st.button("📨 Invia Risultati su Telegram"):
            if not shuffle_results:
                st.error("Fai prima il sorteggio!")
            else:
                with st.spinner("Invio in corso..."):
                    success, log = asyncio.run(send_results_to_group(selected_group_id, BOT_TOKEN))
                    if success:
                        st.success("Processo completato!")
                        st.text_area("Log Invio", log, height=200)
                    else:
                        st.error(log)

with tab5:
    st.header("💬 Invia Messaggi")
    
    msg_scope = st.radio("A chi vuoi scrivere?", ["Gruppo Corrente", "Tutti i Gruppi (Broadcast)"])
    
    recipients = []
    
    if msg_scope == "Gruppo Corrente":
        target_type = st.selectbox("Destinatario", ["Tutti i membri", "Singolo utente"])
        if target_type == "Tutti i membri":
            recipients = [(name, cid) for name, cid in participants.items()]
        else:
            target_user = st.selectbox("Seleziona Utente", list(participants.keys()))
            if target_user:
                recipients = [(target_user, participants[target_user])]
    else:
        st.warning("⚠️ Stai per inviare un messaggio a TUTTI gli utenti di TUTTI i gruppi!")
        # Raccogli tutti gli utenti da tutti i gruppi
        all_groups = load_json(GROUPS_FILE)
        for gid in all_groups:
            g_path = os.path.join(DATA_DIR, gid, "participants.json")
            p = load_json(g_path)
            for name, cid in p.items():
                recipients.append((name, cid))
    
    message_text = st.text_area("Messaggio", height=100)
    
    if st.button("Invia Messaggio 🚀"):
        if not message_text:
            st.error("Scrivi un messaggio!")
        else:
            progress_bar = st.progress(0)
            log_area = st.empty()
            logs = []
            
            count = 0
            for name, chat_id in recipients:
                if isinstance(chat_id, int) or (isinstance(chat_id, str) and chat_id.isdigit()):
                    success, err = asyncio.run(send_telegram_message(chat_id, message_text))
                    if success:
                        logs.append(f"✅ Inviato a {name}")
                    else:
                        logs.append(f"❌ Errore {name}: {err}")
                else:
                    logs.append(f"⚠️ Saltato {name} (No Chat ID valido)")
                
                count += 1
                progress_bar.progress(count / len(recipients))
            
            log_area.text_area("Log Invio", "\n".join(logs))
            st.success("Invio completato!")

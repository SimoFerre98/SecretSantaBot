import streamlit as st
import json
import os
import asyncio
from group_actions import shuffle_group, manage_exclusions
from send_results import send_results_to_group

# Configurazione
GROUPS_FILE = "groups/groups.json"
DATA_DIR = "data"
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

st.title("🎅 Secret Santa Bot Dashboard")

# Sidebar: Selezione Gruppo
if os.path.exists(GROUPS_FILE):
    groups = load_json(GROUPS_FILE)
    group_options = {v['name']: k for k, v in groups.items()}
    
    selected_group_name = st.sidebar.selectbox("Seleziona Gruppo", list(group_options.keys()))
    selected_group_id = group_options[selected_group_name]
    
    st.sidebar.info(f"ID Gruppo: {selected_group_id}")
else:
    st.error("Nessun gruppo trovato.")
    st.stop()

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
tab1, tab2, tab3, tab4 = st.tabs(["👥 Partecipanti", "🎁 Wishlist", "🚫 Esclusioni", "⚙️ Gestione Gioco"])

with tab1:
    st.header("Gestione Partecipanti")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe([{"Nome": name, "Chat ID": cid} for name, cid in participants.items()], use_container_width=True)
    
    with col2:
        st.subheader("Aggiungi Partecipante")
        new_name = st.text_input("Nome")
        new_chat_id = st.text_input("Chat ID (opzionale, per test)")
        if st.button("Aggiungi"):
            if new_name and new_name not in participants:
                participants[new_name] = int(new_chat_id) if new_chat_id.isdigit() else "MANUAL_ENTRY"
                save_json(participants_file, participants)
                
                # Aggiorna anche groups.json
                if new_name not in groups[selected_group_id]["members"]:
                    groups[selected_group_id]["members"].append(new_name)
                    save_json(GROUPS_FILE, groups)
                
                st.success(f"{new_name} aggiunto!")
                st.rerun()
            elif new_name in participants:
                st.warning("Nome già esistente.")

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
            # Simuliamo di essere l'admin per poter lanciare la funzione
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


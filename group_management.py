import os
import json
from utils import load_data, save_data, generate_unique_id

GROUPS_FILE = "groups/groups.json"
GROUPS_DIR = "data"

def create_group(user_name, chat_id=None):
    """Crea un nuovo gruppo e restituisce il suo ID."""
    group_id = generate_unique_id()
    groups = load_data(GROUPS_FILE)

    if group_id not in groups:
        groups[group_id] = {"name": f"Gruppo di {user_name}", "admin": user_name, "members": [user_name]}
        save_data(GROUPS_FILE, groups)

        # Crea la directory del gruppo
        group_path = os.path.join(GROUPS_DIR, group_id)
        os.makedirs(group_path, exist_ok=True)

        # Crea i file JSON del gruppo
        # Se chat_id è None (creato da dashboard), salviamo un placeholder o gestiamo dopo
        participants_data = {user_name: chat_id if chat_id else "DASHBOARD_ADMIN"}
        save_data(os.path.join(group_path, "participants.json"), participants_data)
        save_data(os.path.join(group_path, "exclusions.json"), {})
        save_data(os.path.join(group_path, "wishlist.json"), {})
        save_data(os.path.join(group_path, "shuffle.json"), {})

    return group_id

def join_group(group_id, user_name, chat_id):
    """Aggiunge un utente a un gruppo esistente."""
    groups = load_data(GROUPS_FILE)

    if group_id not in groups:
        return False, "Il gruppo non esiste."

    if user_name not in groups[group_id]["members"]:
        groups[group_id]["members"].append(user_name)
        save_data(GROUPS_FILE, groups)

        # Aggiungi l'utente al file participants.json del gruppo
        group_path = os.path.join(GROUPS_DIR, group_id)
        participants = load_data(os.path.join(group_path, "participants.json"))
        participants[user_name] = chat_id  # Salva il Chat ID invece del ruolo
        save_data(os.path.join(group_path, "participants.json"), participants)

    return True, f"Sei stato aggiunto al gruppo {groups[group_id]['name']}."

def list_user_groups(user_name):
    """Mostra l'elenco dei gruppi a cui un utente appartiene."""
    groups = load_data(GROUPS_FILE)
    user_groups = [
        {"id": group_id, "name": group["name"]}
        for group_id, group in groups.items() if user_name in group["members"]
    ]
    return user_groups

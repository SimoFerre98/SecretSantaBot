import os
import json
from utils import load_data, save_data, generate_unique_id

GROUPS_FILE = "groups/groups.json"
GROUPS_DIR = "data"

def create_group(user_name, group_name, chat_id=None, visibility="public", access_code=None):
    """Crea un nuovo gruppo e restituisce il suo ID e un messaggio."""
    if not group_name:
        return None, "Il nome del gruppo non può essere vuoto."
    
    if visibility == "private" and not access_code:
         return None, "I gruppi privati richiedono un codice di accesso."

    groups = load_data(GROUPS_FILE)
    
    # Check se il nome esiste già
    for g in groups.values():
        if g.get("name") == group_name:
            return None, f"Esiste già un gruppo chiamato '{group_name}'. Scegline un altro."

    group_id = generate_unique_id()
    
    groups[group_id] = {
        "name": group_name, 
        "admin": user_name, 
        "members": [user_name],
        "visibility": visibility, # public o private
        "access_code": access_code, # Solo per gruppi privati
        "pending_requests": [] 
    }
    save_data(GROUPS_FILE, groups)
    
    # Crea la cartella per i dati del gruppo
    group_path = os.path.join(GROUPS_DIR, group_id)
    os.makedirs(group_path, exist_ok=True)
    
    # Crea i file JSON del gruppo
    participants_data = {user_name: chat_id if chat_id else "DASHBOARD_ADMIN"}
    save_data(os.path.join(group_path, "participants.json"), participants_data)
    save_data(os.path.join(group_path, "exclusions.json"), {})
    save_data(os.path.join(group_path, "wishlist.json"), {})
    save_data(os.path.join(group_path, "shuffle.json"), {})
    
    return group_id, f"Gruppo '{group_name}' ({visibility}) creato con successo!"

def get_all_groups():
    """Restituisce una lista di tutti i nomi dei gruppi con visibilità."""
    groups = load_data(GROUPS_FILE)
    group_list = []
    for g in groups.values():
        icon = "🔒" if g.get("visibility") == "private" else "🔓"
        group_list.append(f"{icon} {g['name']}")
    return "\n".join(group_list) if group_list else "Nessun gruppo disponibile."

def join_group(group_id, user_name, chat_id=None, access_code=None):
    """Aggiunge un utente a un gruppo esistente."""
    groups = load_data(GROUPS_FILE)
    
    if group_id in groups:
        group = groups[group_id]
        
        if user_name in group["members"]:
            return True, f"Sei già membro del gruppo '{group['name']}'."
            
        # Logica per gruppi privati
        if group.get("visibility") == "private":
            # Se viene fornito un codice di accesso corretto, entra direttamente
            if access_code and access_code == group.get("access_code"):
                pass # Procedi all'aggiunta
            else:
                # Fallback alla richiesta manuale se il codice è errato o assente
                # Controlla se c'è già una richiesta
                if any(req['user_name'] == user_name for req in group.get("pending_requests", [])):
                    return False, "Hai già inviato una richiesta per questo gruppo. Attendi l'approvazione dell'admin."
                
                # Aggiungi richiesta
                request = {"user_name": user_name, "chat_id": chat_id}
                group.setdefault("pending_requests", []).append(request)
                save_data(GROUPS_FILE, groups)
                return False, "🔒 Questo gruppo è privato. Richiesta inviata all'admin (o riprova con il codice)."

        # Logica per gruppi pubblici (o se approvato/codice corretto)
        group["members"].append(user_name)
        save_data(GROUPS_FILE, groups)
        
        # Salva anche nel file specifico del gruppo
        group_path = os.path.join(GROUPS_DIR, group_id)
        participants_path = os.path.join(group_path, "participants.json")
        participants = load_data(participants_path)
        participants[user_name] = chat_id if chat_id else "member"
        save_data(participants_path, participants)
        
        return True, f"Ti sei unito al gruppo '{group['name']}'!"
    return False, "Gruppo non trovato."

def approve_join_request(group_id, user_name):
    """Approva una richiesta di accesso."""
    groups = load_data(GROUPS_FILE)
    if group_id in groups:
        group = groups[group_id]
        
        # Trova la richiesta
        request = next((req for req in group.get("pending_requests", []) if req["user_name"] == user_name), None)
        if request:
            # Rimuovi richiesta
            group["pending_requests"] = [req for req in group["pending_requests"] if req["user_name"] != user_name]
            
            # Aggiungi ai membri
            group["members"].append(user_name)
            save_data(GROUPS_FILE, groups)
            
            # Salva nel file specifico
            group_path = os.path.join(GROUPS_DIR, group_id)
            participants_path = os.path.join(group_path, "participants.json")
            participants = load_data(participants_path)
            participants[user_name] = request.get("chat_id", "member")
            save_data(participants_path, participants)
            
            return True, request.get("chat_id") # Ritorna chat_id per notifica
    return False, None

def list_user_groups(user_name):
    """Mostra l'elenco dei gruppi a cui un utente appartiene."""
    groups = load_data(GROUPS_FILE)
    user_groups = [
        {"id": group_id, "name": group["name"]}
        for group_id, group in groups.items() if user_name in group["members"]
    ]
    return user_groups

def save_wishlist(group_id, user_name, wish):
    """Salva il desiderio di un utente nella wishlist del gruppo."""
    group_path = os.path.join(GROUPS_DIR, group_id)
    wishlist_path = os.path.join(group_path, "wishlist.json")
    
    wishlist = load_data(wishlist_path)
    wishlist[user_name] = wish
    save_data(wishlist_path, wishlist)
    return True

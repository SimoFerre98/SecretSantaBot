import os
from utils import load_data, save_data
from utils import send_response

def shuffle_group(group_id, user_name):
    """Esegue il sorteggio per il gruppo (solo admin)."""
    group_path = f"data/{group_id}"
    participants = load_data(os.path.join(group_path, "participants.json"))
    exclusions = load_data(os.path.join(group_path, "exclusions.json"))

    if participants[user_name] != "admin":
        return "Non sei autorizzato a eseguire il sorteggio."

    import random
    givers = list(participants.keys())
    receivers = givers.copy()
    random.shuffle(receivers)

    pairs = {}
    for giver in givers:
        possible_receivers = [r for r in receivers if r != giver and r not in exclusions.get(giver, [])]
        if not possible_receivers:
            return "Impossibile completare il sorteggio con le esclusioni attuali."
        receiver = random.choice(possible_receivers)
        pairs[giver] = receiver
        receivers.remove(receiver)

    save_data(os.path.join(group_path, "shuffle.json"), pairs)
    return "Sorteggio completato!"

def show_participants(group_id):
    """Mostra i partecipanti di un gruppo."""
    groups = load_data("groups/groups.json")
    if group_id in groups:
        members = groups[group_id].get("members", [])
        return "\n".join(members)
    return ""

def add_to_wishlist(group_id, user_name, wish):
    """Aggiunge un elemento alla wishlist dell'utente."""
    group_path = f"data/{group_id}"
    wishlist = load_data(os.path.join(group_path, "wishlist.json"))
    wishlist[user_name] = wish
    save_data(os.path.join(group_path, "wishlist.json"), wishlist)
    return "Wishlist aggiornata!"

def manage_exclusions(group_id, user_name, exclusion_name):
    """Aggiunge o rimuove un'esclusione per l'utente."""
    group_path = f"data/{group_id}"
    exclusions = load_data(os.path.join(group_path, "exclusions.json"))

    if user_name not in exclusions:
        exclusions[user_name] = []

    if exclusion_name in exclusions[user_name]:
        exclusions[user_name].remove(exclusion_name)
        message = f"{exclusion_name} rimosso dalle tue esclusioni."
    else:
        exclusions[user_name].append(exclusion_name)
        message = f"{exclusion_name} aggiunto alle tue esclusioni."

    save_data(os.path.join(group_path, "exclusions.json"), exclusions)
    return message

async def participants(update, context):
    """Mostra i partecipanti del gruppo attivo."""
    group_id = context.user_data.get("current_group")
    if not group_id:
        response = "Devi prima accedere a un gruppo."
    else:
        participant_list = show_participants(group_id)
        response = f"Partecipanti del gruppo:\n{participant_list}"

    # Usa la funzione send_response per gestire il contesto
    await send_response(update, response)
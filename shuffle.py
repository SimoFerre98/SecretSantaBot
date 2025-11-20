import os
import json
import random

# Percorso della cartella del gruppo
GROUP_FOLDER = "data/5b506af4-2cfe-4486-ba6e-99358923838f"  # Sostituisci <group_id> con l'ID del gruppo

def load_data(filename):
    """Carica i dati da un file JSON."""
    filepath = os.path.join(GROUP_FOLDER, filename)
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(filename, data):
    """Salva i dati in un file JSON."""
    filepath = os.path.join(GROUP_FOLDER, filename)
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def secret_santa():
    """Esegue il sorteggio Secret Santa rispettando le esclusioni."""
    participants = load_data("participants.json")  # Carica i partecipanti
    exclusions = load_data("exclusions.json")  # Carica le esclusioni

    givers = list(participants.keys())
    receivers = givers.copy()
    random.shuffle(receivers)

    pairs = {}
    for giver in givers:
        possible_receivers = [r for r in receivers if r != giver and r not in exclusions.get(giver, [])]
        if not possible_receivers:
            print("Errore: Non è possibile completare il sorteggio con le esclusioni attuali.")
            return None
        receiver = random.choice(possible_receivers)
        pairs[giver] = receiver
        receivers.remove(receiver)

    # Salva i risultati nel file shuffle.json
    save_data("shuffle.json", pairs)
    print("Sorteggio completato! Risultati salvati in shuffle.json.")
    return pairs

if __name__ == "__main__":
    secret_santa()

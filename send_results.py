from telegram import Bot
import os
import json
import asyncio

def load_data(filepath):
    """Carica i dati da un file JSON."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {filepath} non trovato.")
        return {}

async def send_results_to_group(group_id, bot_token):
    """Invia i risultati del sorteggio ai partecipanti di un gruppo specifico."""
    bot = Bot(token=bot_token)
    group_folder = f"data/{group_id}"

    # Carica i dati
    participants_path = os.path.join(group_folder, "participants.json")
    shuffle_path = os.path.join(group_folder, "shuffle.json")
    
    participants = load_data(participants_path)  # ID dei partecipanti
    shuffle_results = load_data(shuffle_path)  # Risultati del sorteggio

    if not shuffle_results:
        return False, "Errore: Nessun risultato trovato. Esegui prima il sorteggio."

    results_log = []
    for giver, receiver in shuffle_results.items():
        chat_id = participants.get(giver)
        
        # Gestione caso in cui il partecipante ha un ruolo (es. "admin") invece che chat_id diretto
        # O se il formato è diverso. Assumiamo che participants.json mappi Nome -> ChatID o Nome -> Ruolo
        # Se mappa Nome -> Ruolo, dobbiamo trovare il ChatID da qualche altra parte?
        # Guardando bot.py: participants[user_name] = chat_id (in secret_santa_bot.py)
        # MA in group_management.py: participants[user_name] = "admin" o "member".
        # C'è un problema: group_management.py NON salva i Chat ID!
        # Dobbiamo risolvere questo problema. Per ora mantengo la logica ma segnalo il problema.
        
        # In group_management.py riga 22 e 43 salviamo solo il ruolo.
        # Dobbiamo salvare anche il Chat ID quando uno fa /joingroup.
        
        if not isinstance(chat_id, int) and not (isinstance(chat_id, str) and chat_id.isdigit()):
             # Fallback: proviamo a vedere se c'è un altro file o se dobbiamo cambiare la logica di join
             # Per ora logghiamo l'errore, ma questo è un bug preesistente che la dashboard evidenzierà.
             results_log.append(f"⚠️ Impossibile inviare a {giver}: Chat ID mancante (Trovato: {chat_id})")
             continue

        message = f"Ciao {giver}, sei il Secret Santa di: {receiver}! 🎁"
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            results_log.append(f"✅ Messaggio inviato a {giver}.")
        except Exception as e:
            results_log.append(f"❌ Errore invio a {giver}: {e}")
            
    return True, "\n".join(results_log)

if __name__ == "__main__":
    # Esempio di utilizzo (da sostituire con input reali se eseguito direttamente)
    # asyncio.run(send_results_to_group("ID_GRUPPO", "TOKEN"))
    pass

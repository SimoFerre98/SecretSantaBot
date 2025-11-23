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
    wishlist_path = os.path.join(group_folder, "wishlist.json")
    
    participants = load_data(participants_path)  # ID dei partecipanti
    shuffle_results = load_data(shuffle_path)  # Risultati del sorteggio
    wishlist = load_data(wishlist_path) # Wishlist

    if not shuffle_results:
        return False, "Errore: Nessun risultato trovato. Esegui prima il sorteggio."

    results_log = []
    for giver, receiver in shuffle_results.items():
        chat_id = participants.get(giver)
        
        if not isinstance(chat_id, int) and not (isinstance(chat_id, str) and chat_id.isdigit()):
             results_log.append(f"⚠️ Impossibile inviare a {giver}: Chat ID mancante (Trovato: {chat_id})")
             continue

        message = f"Ciao {giver}, sei il Secret Santa di: {receiver}! 🎁"
        
        # Aggiungi wishlist se presente
        receiver_wish = wishlist.get(receiver)
        if receiver_wish:
            message += f"\n\n📝 **La sua Wishlist:**\n{receiver_wish}"
        else:
            message += "\n\n(Non ha specificato desideri particolari)"

        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            results_log.append(f"✅ Messaggio inviato a {giver}.")
        except Exception as e:
            results_log.append(f"❌ Errore invio a {giver}: {e}")
            
    return True, "\n".join(results_log)

if __name__ == "__main__":
    # Esempio di utilizzo (da sostituire con input reali se eseguito direttamente)
    # asyncio.run(send_results_to_group("ID_GRUPPO", "TOKEN"))
    pass

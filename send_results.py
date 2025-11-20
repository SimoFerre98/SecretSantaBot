from telegram import Bot
import os
import json
import asyncio

# Configura il token del bot e la cartella del gruppo
BOT_TOKEN = "7548642306:AAFIFgN95ntOFGdcI2-sHS7T3y3zCCut4R8"
GROUP_FOLDER = "data/5b506af4-2cfe-4486-ba6e-99358923838f" 



def load_data(filename):
    """Carica i dati da un file JSON."""
    filepath = os.path.join(GROUP_FOLDER, filename)
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {filename} non trovato.")
        return {}

async def send_results():
    """Invia i risultati del sorteggio ai partecipanti."""
    bot = Bot(token=BOT_TOKEN)

    # Carica i dati
    participants = load_data("participants.json")  # ID dei partecipanti
    shuffle_results = load_data("shuffle.json")  # Risultati del sorteggio

    if not shuffle_results:
        print("Errore: Nessun risultato trovato. Esegui prima il sorteggio.")
        return

    for giver, receiver in shuffle_results.items():
        chat_id = participants.get(giver)
        if chat_id is None:
            print(f"Errore: Nessun ID trovato per {giver}.")
            continue

        # Messaggio da inviare
        message = f"Ciao {giver}, sei il Secret Santa di: {receiver}! 🎁"
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            print(f"Messaggio inviato a {giver}.")
        except Exception as e:
            print(f"Errore nell'invio del messaggio a {giver} (ID: {chat_id}): {e}")

if __name__ == "__main__":
    asyncio.run(send_results())

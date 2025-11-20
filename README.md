# SecretSantaBot

SecretSantaBot è un progetto in Python che gestisce il gioco del Secret Santa tramite un bot Telegram e una dashboard web. Consente di creare gruppi, aggiungere partecipanti, definire esclusioni, eseguire il sorteggio e inviare i risultati direttamente su Telegram.

## Cosa fa
- Crea e gestisce gruppi con admin e membri
- Salva i dati dei partecipanti e le loro wishlist in file JSON
- Gestisce esclusioni tra coppie (chi non deve regalare a chi)
- Esegue lo shuffle rispettando le esclusioni
- Invia messaggi e risultati del sorteggio ai partecipanti via Telegram
- Offre una dashboard Streamlit per amministrare il gioco

## Requisiti
- Python 3.10+
- Pacchetti: `python-telegram-bot`, `streamlit`

Installa i pacchetti necessari:

```
pip install python-telegram-bot streamlit
```

## Configurazione
- Recupera il tuo token del bot da BotFather su Telegram
- Imposta il token nel codice:
  - `bot.py`: sostituisci il token nel builder `Application.builder().token("...")`
  - `dashboard.py`: aggiorna `BOT_TOKEN = "..."`

Facoltativo: puoi organizzare i dati dei gruppi nella cartella `data/` (creata automaticamente). I metadati dei gruppi sono in `groups/groups.json`.

## Come usarlo

### Avviare il bot Telegram
1. Avvia il bot:
   ```
   python bot.py
   ```
2. Comandi disponibili sul bot:
   - `/start` benvenuto
   - `/creategroup` crea un nuovo gruppo e imposta l’admin
   - `/joingroup <ID_GRUPPO>` entra in un gruppo esistente
   - `/participants` mostra i partecipanti del gruppo attivo
   - `/back` torna al menu gruppi

### Usare la dashboard
1. Avvia la dashboard Streamlit:
   ```
   streamlit run dashboard.py
   ```
2. Dalla sidebar puoi:
   - Attivare/disattivare il bot (toggle)
   - Selezionare un gruppo esistente o crearne uno nuovo
3. Dalle tab puoi:
   - Gestire partecipanti (aggiungere/rimuovere, promuovere admin)
   - Modificare wishlist
   - Gestire esclusioni
   - Eseguire il sorteggio (shuffle) e inviare i risultati su Telegram
   - Inviare messaggi al gruppo corrente o broadcast a tutti i gruppi

### Struttura dati
- `groups/groups.json`: elenco gruppi, admin e membri
- `data/<group_id>/participants.json`: mappa `Nome -> ChatID`
- `data/<group_id>/exclusions.json`: esclusioni per utente
- `data/<group_id>/wishlist.json`: desideri per utente
- `data/<group_id>/shuffle.json`: risultati del sorteggio

### Script di utilità
- `shuffle.py`: esempio di sorteggio standalone su una cartella di gruppo
- `send_results.py`: invio dei risultati del sorteggio su Telegram per un gruppo

## Note
- Assicurati che ogni partecipante abbia un `ChatID` valido in `participants.json` prima di inviare i risultati
- Le cartelle e i file JSON sono generati automaticamente quando crei o modifichi gruppi dalla dashboard o dal bot
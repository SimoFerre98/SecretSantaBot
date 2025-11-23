# 🎅 Secret Santa Bot & Dashboard

Benvenuto nel progetto **Secret Santa Bot**! Questo sistema ti permette di organizzare facilmente lo scambio di regali tra amici, colleghi o familiari usando Telegram e una comoda Dashboard Web.

## 🚀 Funzionalità Principali

### 🤖 Bot Telegram
- **Creazione Gruppi**: Crea gruppi pubblici o privati.
- **Gestione Partecipanti**: Unisciti ai gruppi e vedi chi partecipa.
- **Wishlist**: Inserisci i tuoi desideri direttamente dal bot.
- **Mini App**: Un'interfaccia grafica festiva integrata (anteprima locale).
- **Notifiche**: Ricevi il nome del tuo "Secret Santa" direttamente in chat.

### 📊 Dashboard Web (Streamlit)
- **Gestione Completa**: L'admin può vedere tutti i gruppi e i partecipanti.
- **Esclusioni**: Imposta regole (es. "Marco non può regalare a Giulia").
- **Shuffle**: Esegui il sorteggio automatico delle coppie.
- **Invio Risultati**: Invia i messaggi a tutti con un click.

## 🛠️ Installazione e Avvio

### Prerequisiti
- Python 3.8+
- Un token bot Telegram (da `@BotFather`)

### Avvio Rapido
Per lanciare sia il Bot che la Dashboard contemporaneamente:

```bash
python run_all.py
```

- **Dashboard**: http://localhost:8501
- **Mini App (Anteprima)**: http://localhost:8000

## 📂 Struttura del Progetto

- `src/`: Contiene tutto il codice sorgente (Bot, Dashboard, Logica).
- `webapp/`: Frontend della Mini App (HTML/CSS/JS).
- `data/`: Cartella dove vengono salvati i dati dei gruppi (JSON).
- `run_all.py`: Script per avviare tutto.

## 📝 Note
- Il bot supporta gruppi **Pubblici** (accesso libero) e **Privati** (approvazione admin).
- La Mini App richiede HTTPS per funzionare su Telegram, ma può essere testata in locale.

Buon divertimento e Buon Natale! 🎄
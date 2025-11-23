import subprocess
import sys
import time

def run_all():
    print("🚀 Avvio Secret Santa Bot e Dashboard...")

    # Avvia il bot Telegram
    bot_process = subprocess.Popen([sys.executable, "src/bot.py"])
    print(f"🤖 Bot avviato (PID: {bot_process.pid})")

    # Avvia la dashboard Streamlit
    dashboard_process = subprocess.Popen(["streamlit", "run", "src/dashboard.py"])
    print(f"📊 Dashboard avviata (PID: {dashboard_process.pid})")

    try:
        # Mantieni lo script in esecuzione finché uno dei processi non termina
        while True:
            if bot_process.poll() is not None:
                print("⚠️ Il bot si è fermato!")
                break
            if dashboard_process.poll() is not None:
                print("⚠️ La dashboard si è fermata!")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arresto in corso...")
    finally:
        bot_process.terminate()
        dashboard_process.terminate()
        print("✅ Tutti i processi terminati.")

if __name__ == "__main__":
    run_all()

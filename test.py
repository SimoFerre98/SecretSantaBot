from telegram import Bot
import asyncio

BOT_TOKEN = "7548642306:AAFIFgN95ntOFGdcI2-sHS7T3y3zCCut4R8"
TEST_CHAT_ID = 5164798065  # Sostituisci con il tuo ID

async def send_test_message():
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=TEST_CHAT_ID, text="é arrivato il pacco amazon con i tuoi dischetti")
        print(f"Messaggio inviato con successo a ID: {TEST_CHAT_ID}")
    except Exception as e:
        print(f"Errore nell'invio del messaggio a ID {TEST_CHAT_ID}: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_message())

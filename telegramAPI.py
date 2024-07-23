import telegram, asyncio, dotenv, os
# from telegram import ParseMode

dotenv.load_dotenv()

bot = telegram.Bot(os.getenv("TELEGRAM_TOKEN"))
chatIds = ["879805663"]

def sendMessage(text, sendTo=0):
  try:
      loop = asyncio.get_event_loop()
  except RuntimeError:
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)

  if sendTo == "a":
    for chatId in chatIds:
      loop.run_until_complete(bot.send_message(chat_id=chatId, text=text, parse_mode="HTML"))
  else:
    loop.run_until_complete(bot.send_message(chat_id=chatIds[sendTo], text=text, parse_mode="HTML"))

if __name__ == "__main__":
  sendMessage("Hello")
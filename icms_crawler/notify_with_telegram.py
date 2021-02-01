import telegram
from telegram.error import NetworkError, Unauthorized

CHAT_ID='000000000'
TOKEN='0000000000:0000000000000000000000000000000000'

def notify(msg):
	#msg=msg.replace("\\n","\n")
	bot = telegram.Bot(TOKEN)
	bot.sendMessage(chat_id=CHAT_ID, text=msg, parse_mode="markdown")

def notify_with_imagepath(imagepath, msg=None):
	#msg=msg.replace("\\n","\n")
	bot=telegram.Bot(TOKEN)
	bot.send_photo(chat_id=CHAT_ID, photo=open(imagepath, 'rb'), caption=msg, parse_mode="markdown")

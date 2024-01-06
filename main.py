import os
import time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from decouple import config
import functools
from keep_alive import keep_alive

# Configuration
TOKEN = config("BOT_TOKEN", default=None, cast=str)
FORWARD_TO_CHANNELS = config("FORWARD_TO_CHANNELS", default="", cast=str)
SLEEP_TIME = config("SLEEP_TIME", default=10, cast=int)
ADMINS = config("ADMIN_IDS", default="")
ADMIN_IDS = [int(i) for i in ADMINS.split()]

keep_alive()

LINKS_MESSAGE= '''
✅🔞 All Channel 🔞✅

⏬⬇️ BACKUP CHANNEL ⬇️⏬
🔥 https://t.me/backup_wallah 🔥

✅🔞 All Private Channels 🔞✅
🔥 https://t.me/Oyo_room_leaked_viral_videos_bot 🔥

🔥 https://t.me/+YSo-jCnTz6E5MzE1 🔥

🔥 https://t.me/Desi_viral_hindi_mms_videos_xbot 🔥

🔥 https://t.me/+yrPJwAqKC8dkY2Rl 🔥
'''



# Global variables
is_forwarding = False
channel_index = 0  # New global variable to track channel index
WHITELISTED_TEXTS = ["teraboxapp.com/s/", "t.me/backup_wallah"]

# Bot instance
bot = Bot(token=TOKEN)

try:
    os.makedirs("data")
except OSError:
    pass

def admin_required(func):
    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext) -> None:
        if update.effective_user.id not in ADMIN_IDS:
            update.message.reply_text("Sorry, you don't have permission to use this bot.")
            return
        return func(update, context)
    return wrapper

@admin_required
def start(update: Update, context: CallbackContext) -> None:
    """
    Start command handler
    """
    update.message.reply_text("Hello! I'm alive. Send /forward to start forwarding.")


@admin_required
def links(update: Update, context: CallbackContext) -> None:
    """
    Send links command handler
    """
    channels = FORWARD_TO_CHANNELS.split(",")
    for channel_id in channels:
        bot.send_message(chat_id=channel_id, text=LINKS_MESSAGE, parse_mode=None, disable_web_page_preview=True)  # Add parse_mode=None
    update.message.reply_text("Links message sent to all channels.")


@admin_required
def message_received(update: Update, context: CallbackContext) -> None:
    """
    Message handler
    """
    global channel_index

    if is_forwarding:
        channel_id = FORWARD_TO_CHANNELS.split(",")[channel_index]

        # Handle text messages
        if update.message.text:
            bot.send_message(chat_id=channel_id, text=update.message.text)
            update.message.reply_text("Message forwarded to channel {}".format(channel_id))

        # Handle photos with captions
        elif update.message.photo and update.message.caption:
            if all(text in update.message.caption for text in WHITELISTED_TEXTS):
                photo = bot.get_file(update.message.photo[-1].file_id)
                file_name = os.path.join("data", photo.file_path.split("/")[-1])
                photo.download(file_name)
                bot.send_photo(
                    chat_id=channel_id,
                    photo=open(file_name, "rb"),
                    caption=update.message.caption,
                )
                os.remove(file_name)
                update.message.reply_text("Message forwarded to channel {}".format(channel_id))
            else:
                update.message.reply_text("Message not forwarded: Missing required texts in caption.")

        # Handle videos with captions (adjust for other media types)
        elif update.message.video and update.message.caption:
            if all(text in update.message.caption for text in WHITELISTED_TEXTS):
                video = bot.get_file(update.message.video.file_id)
                file_name = os.path.join("data", video.file_path.split("/")[-1])
                video.download(file_name)
                bot.send_video(
                    chat_id=channel_id,
                    video=open(file_name, "rb"),
                    caption=update.message.caption,
                )
                os.remove(file_name)
                update.message.reply_text("Message forwarded to channel {}".format(channel_id))

        channel_index = (channel_index + 1) % len(FORWARD_TO_CHANNELS.split(","))  # Increment and wrap around
        time.sleep(SLEEP_TIME)
    else:
        update.message.reply_text("Start forwarding with /forward before sending messages.")

@admin_required
def forward(update: Update, context: CallbackContext) -> None:
    """
    Start forwarding messages
    """
    global is_forwarding
    is_forwarding = True
    update.message.reply_text("Forwarding messages is now active.")

@admin_required
def stop(update: Update, context: CallbackContext) -> None:
    """
    Stop forwarding messages
    """
    global is_forwarding
    is_forwarding = False
    update.message.reply_text("Forwarding messages is now inactive.")


def main():
    """
    Main function
    """
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("forward", forward))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("links", links))
    dispatcher.add_handler(MessageHandler(Filters.all, message_received))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from discord_webhook import DiscordWebhook, DiscordEmbed

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram bot token
BOT_TOKEN = '7330349324:AAHqE_aDS-WlNSVTLDEemWAC3gQBRKRbbDc'

# Discord webhook URL
WEBHOOK_URL = 'https://discord.com/api/webhooks/1252787799942496277/XsYLzd6nARRdP84_qsXNgxMVf1deQ5XbW2GOMpX-DPnSHC5KmlvY7DjKzPUBdrZ0me6o'

# Path to the data file
DATA_FILE = 'trading_data.json'

def load_trading_data():
    try:
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            return data.get('trades', [])
    except FileNotFoundError:
        logger.error(f"File '{DATA_FILE}' tidak ditemukan.")
        return []
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat memuat data: {str(e)}")
        return []

def get_coin_pnl(trades):
    coin_pnl_list = []
    for trade in trades:
        coin = trade.get('symbol', 'Unknown')
        pnl = trade.get('pnl', 0.0)
        link = trade.get('link', 'No link available')
        date = trade.get('date', 'Unknown')
        action = trade.get('action', 'Unknown')
        coin_pnl_list.append((coin, pnl, link, date, action))
    return coin_pnl_list

def send_coin_pnl_to_discord(coin_pnl_list):
    if not coin_pnl_list:
        logger.error("Tidak ada data untuk dikirim ke Discord.")
        return
    
    embed = DiscordEmbed(title="Trading Report", color=0x00ff00)  # Warna hijau untuk laporan trading
    embed.set_author(name="Bot REKT", url="https://i.ytimg.com/vi/DCipyjzy9bs/maxresdefault.jpg", icon_url="https://i.ytimg.com/vi/DCipyjzy9bs/maxresdefault.jpg")
    embed.set_thumbnail(url="https://i.ytimg.com/vi/DCipyjzy9bs/maxresdefault.jpg")
    embed.set_footer(text="Bot REKT", icon_url="https://i.ytimg.com/vi/DCipyjzy9bs/maxresdefault.jpg")
    embed.set_timestamp()

    for coin, pnl, link, date, action in coin_pnl_list:
        embed.add_embed_field(name=f"{coin} ({action})", value=f"**PNL**: {pnl:.2f} $\n**Date**: {date}\n**Setup**: {link}", inline=False)

    webhook = DiscordWebhook(url=WEBHOOK_URL, content='Daftar Nama Coin dan PNL:')
    webhook.add_embed(embed)

    response = webhook.execute()

    if response.status_code == 204:
        logger.info("Data berhasil dikirim ke Discord.")
    else:
        logger.error(f"Terjadi kesalahan: {response.status_code}, {response.text}")

async def get(update: Update, context: CallbackContext):
    logger.info("Received /get command")
    trades = load_trading_data()
    coin_pnl_list = get_coin_pnl(trades)
    send_coin_pnl_to_discord(coin_pnl_list)
    await update.message.reply_text("Trading report has been sent to Discord.")

if __name__ == '__main__':
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        get_handler = CommandHandler('get', get)
        application.add_handler(get_handler)

        logger.info("Bot is running...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Error running the application: {e}")

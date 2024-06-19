import ccxt
import telebot
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Telegram bot token from environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Initialize Bybit exchange via CCTX
bybit = ccxt.bybit({
    'apiKey': 'zwMY9Di75MxTg3zgdP',
    'secret': 'EenXgsDdXoigyMylbQpnlCliAf0wU25yb88p',
})

# Initialize Telegram bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Function to get open positions from Bybit
def get_open_positions():
    try:
        positions = bybit.fetch_positions()
        return positions
    except ccxt.NetworkError as e:
        print(f"Network error: {str(e)}")
        return None
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {str(e)}")
        return None

# Command handler for /positions command
@bot.message_handler(commands=['positions'])
def send_positions(message):
    positions = get_open_positions()

    if positions is None:
        bot.reply_to(message, "Failed to fetch positions from Bybit.")
        return

    if len(positions) == 0:
        bot.reply_to(message, "No open positions.")
    else:
        response = "Open positions on Bybit:\n\n"
        for position in positions:
            # Use get() method to avoid KeyError
            symbol = position.get('symbol', 'N/A')
            side = position.get('side', 'N/A')
            size = position.get('size', 'N/A')
            entry_price = position.get('entry_price', 'N/A')
            current_price = position.get('current_price', 'N/A')

            response += f"Symbol: {symbol}\n"
            response += f"Side: {side}\n"
            response += f"Size: {size}\n"
            response += f"Entry Price: {entry_price}\n"
            response += f"Current Price: {current_price}\n"
            response += "\n"

        bot.reply_to(message, response)

# Start the bot
if __name__ == "__main__":
    bot.polling()

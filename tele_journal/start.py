import requests
import matplotlib.pyplot as plt
import numpy as np
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
import json
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WEBHOOK_URL = 'https://discord.com/api/webhooks/1252787899024408587/JBHuxPMz9Nsfn0dcH_Rpd02047rHrJmNF3RW48PL-uMVwPtajqmn9yacg_8GcVHOcFsS'
DATA_FILE = 'trading_data.json'
BOT_TOKEN = '7318642228:AAHSzxK2jp_8Lu1IDudKUCc4VEMLuCFD6kQ'

SYMBOL, ACTION, PNL, TV_IDEA_LINK, CONFIRMATION = range(5)

def load_trade_journal():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            return data.get('trades', []), data.get('start_balance', 0.0)
    else:
        start_balance = 0.0
        return [], start_balance

def save_trade_journal(trades, start_balance):
    data = {'trades': trades, 'start_balance': start_balance}
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

async def start(update: Update, context: CallbackContext) -> int:
    logger.info("Received /start command")
    await update.message.reply_text("Welcome to the trading journal bot! Let's start inputting a new trade. Enter the symbol (coin) for the trade:")
    return SYMBOL

async def symbol(update: Update, context: CallbackContext) -> int:
    context.user_data['symbol'] = update.message.text
    await update.message.reply_text("Enter action (L/S) for the trade:")
    return ACTION

async def action(update: Update, context: CallbackContext) -> int:
    context.user_data['action'] = update.message.text
    await update.message.reply_text("Enter PNL for the trade:")
    return PNL

async def pnl(update: Update, context: CallbackContext) -> int:
    context.user_data['pnl'] = float(update.message.text)
    await update.message.reply_text("Enter TradingView idea link for the trade:")
    return TV_IDEA_LINK

async def tv_idea_link(update: Update, context: CallbackContext) -> int:
    context.user_data['tv_idea_link'] = update.message.text
    await update.message.reply_text(f"Review the trade:\n\n"
                              f"Symbol: {context.user_data['symbol']}\n"
                              f"Action: {context.user_data['action']}\n"
                              f"PNL: {context.user_data['pnl']}\n"
                              f"TradingView Idea Link: {context.user_data['tv_idea_link']}\n\n"
                              "Is this correct? (yes/no)")
    return CONFIRMATION

async def confirmation(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'yes':
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        new_trade = {
            "date": today_date,
            "symbol": context.user_data['symbol'],
            "action": context.user_data['action'],
            "pnl": context.user_data['pnl'],
            "link": context.user_data['tv_idea_link']
        }
        existing_trades, start_balance = load_trade_journal()
        all_trades = existing_trades + [new_trade]
        save_trade_journal(all_trades, start_balance)
        send_to_discord(all_trades, start_balance)
        await update.message.reply_text("Trade has been recorded and sent to Discord.")
    else:
        await update.message.reply_text("Trade input has been canceled.")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Trade input canceled.')
    return ConversationHandler.END

def calculate_totals(trades):
    total_pnl = sum(trade["pnl"] for trade in trades)
    win_trades = sum(1 for trade in trades if trade["pnl"] > 0)
    total_trades = len(trades)
    win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0
    total_buy = sum(1 for trade in trades if trade["action"].upper() == "L")
    total_sell = sum(1 for trade in trades if trade["action"].upper() == "S")
    return total_pnl, win_rate, total_trades, total_buy, total_sell

def plot_pnl_graph(trades, start_balance):
    dates = [trade["date"] for trade in trades]
    pnls = [trade["pnl"] for trade in trades]
    cumulative_pnl = np.cumsum(pnls) + start_balance

    unique_dates = sorted(set(dates))
    daily_pnls = []
    current_pnl = start_balance
    
    for date in unique_dates:
        pnl_daily = sum(trade["pnl"] for trade in trades if trade["date"] == date)
        current_pnl += pnl_daily
        daily_pnls.append(current_pnl)

    plt.figure(figsize=(12, 6))
    plt.plot(unique_dates, daily_pnls, marker='o', linestyle='-', color='b', label='Cumulative PNL')
    plt.scatter(unique_dates, daily_pnls, color='b')
    
    for date, pnl in zip(unique_dates, daily_pnls):
        plt.text(date, pnl, f"${pnl:.2f}", ha='center', va='bottom', fontsize=9)

    plt.title('Cumulative PNL Over Time (Daily)', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative PNL', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    plt.savefig('pnl_graph.png')
    plt.close()

def send_to_discord(trades, start_balance):
    total_pnl, win_rate, total_trades, total_buy, total_sell = calculate_totals(trades)
    plot_pnl_graph(trades, start_balance)
    total_balance = start_balance + total_pnl

    embed = DiscordEmbed(title="JOURNAL REKT", color=242424)
    embed.set_author(name="Bot REKT", url="https://i.ytimg.com/vi/DCipyjzy9bs/maxresdefault.jpg", icon_url="https://i.ytimg.com/vi/DCipyjzy9bs/maxresdefault.jpg")
    embed.add_embed_field(name="**TOTAL PNL**", value=f"${total_pnl:.2f}", inline=True)
    embed.add_embed_field(name="**WIN RATE**", value=f"{win_rate:.2f}%", inline=True)
    embed.add_embed_field(name="**TOTAL TRADES**", value=f"{total_trades}", inline=True)
    embed.add_embed_field(name="**LONG**", value=f"{total_buy}", inline=True)
    embed.add_embed_field(name="**SHORT**", value=f"{total_sell}", inline=True)
    embed.add_embed_field(name="**TOTAL BALANCE**", value=f"${total_balance:.2f}", inline=True)

    webhook = DiscordWebhook(url=WEBHOOK_URL, content='Here is the latest trading journal update:')
    with open("pnl_graph.png", "rb") as f:
        webhook.add_file(file=f.read(), filename='pnl_graph.png')

    webhook.add_embed(embed)
    try:
        response = webhook.execute()

        os.remove('pnl_graph.png')

        if response.status_code == 204:
            logger.info("Message successfully sent to Discord")
        elif response.status_code == 200:
            logger.info("Message successfully sent to Discord with status code 200")
        else:
            logger.error(f"Error sending message to Discord: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"Exception occurred while sending message to Discord: {e}")

if __name__ == '__main__':
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SYMBOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, symbol)],
                ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, action)],
                PNL: [MessageHandler(filters.TEXT & ~filters.COMMAND, pnl)],
                TV_IDEA_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, tv_idea_link)],
                CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        application.add_handler(conv_handler)

        logger.info("Bot is running...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Error running the application: {e}")

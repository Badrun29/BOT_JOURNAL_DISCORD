import requests
import matplotlib.pyplot as plt
import numpy as np
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
import json
import datetime
import mplfinance as mpf

WEBHOOK_URL = 'https://discord.com/api/webhooks/1252787899024408587/JBHuxPMz9Nsfn0dcH_Rpd02047rHrJmNF3RW48PL-uMVwPtajqmn9yacg_8GcVHOcFsS'
DATA_FILE = 'trading_data.json'

def load_trade_journal():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            return data.get('trades', []), data.get('start_balance', 0.0)
    else:
        start_balance = float(input("Enter starting balance: "))
        return [], start_balance

def save_trade_journal(trades, start_balance):
    data = {'trades': trades, 'start_balance': start_balance}
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

def input_new_trades():
    trades = []
    n = int(input("Enter number of new trades: "))
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    
    for i in range(n):
        symbol = input(f"Enter symbol (coin) for trade {i+1}: ")
        action = input(f"Enter action (L/S) for trade {i+1}: ")
        pnl = float(input(f"Enter PNL for trade {i+1}: "))
        tv_idea_link = input(f"Enter TradingView idea link for trade {i+1} ")
        trades.append({"date": today_date, "symbol": symbol, "action": action, "pnl": pnl, "link": tv_idea_link})
    
    return trades

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
    daily_pnls_dict = {date:[] for date in unique_dates}
    
    for date in unique_dates:
        # Hitung PNL harian berdasarkan trade pada tanggal tersebut
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

    # Membuat pesan embed Discord
    embed = DiscordEmbed(title="JOURNAL REKT", color=242424)

    # Menambahkan field sebagai tabel dalam pesan embed
    embed.set_author(name="Bot REKT", url="https://i.ytimg.com/vi/DCipyjzy9bs/maxresdefault.jpg", icon_url="https://i.ytimg.com/vi/DCipyjzy9bs/maxresdefault.jpg")
    embed.add_embed_field(name="**TOTAL PNL** 💰", value=f"${total_pnl:.2f}", inline=True)
    embed.add_embed_field(name="**WIN RATE** 📈", value=f"{win_rate:.2f}%", inline=True)
    embed.add_embed_field(name="**TOTAL TRADES** 📊", value=f"{total_trades}", inline=True)
    embed.add_embed_field(name="**LONG** 📥", value=f"{total_buy}", inline=True)
    embed.add_embed_field(name="**SHORT** 📤", value=f"{total_sell}", inline=True)
    embed.add_embed_field(name="**TOTAL BALANCE** 💵", value=f"${total_balance:.2f}", inline=True)

    # Mengirim gambar grafik PNL sebagai lampiran
    webhook = DiscordWebhook(url=WEBHOOK_URL, content='Here is the latest trading journal update:')
    with open("pnl_graph.png", "rb") as f:
        webhook.add_file(file=f.read(), filename='pnl_graph.png')

    # Menetapkan gambar grafik sebagai gambar embed
    embed.set_image(url='attachment://pnl_graph.png')
    webhook.add_embed(embed)
    response = webhook.execute()

    # Menghapus file grafik setelah dikirim
    os.remove('pnl_graph.png')

    # Memeriksa respons webhook untuk memberikan umpan balik
    if response.status_code == 204:
        print("Pesan berhasil dikirim ke Discord")
    elif response.status_code == 200:
        print("Pesan berhasil dikirim ke Discord dengan kode status 200")
    else:
        print(f"Terjadi kesalahan: {response.status_code}, {response.text}")


existing_trades, start_balance = load_trade_journal()
new_trades = input_new_trades()
all_trades = existing_trades + new_trades
save_trade_journal(all_trades, start_balance)
send_to_discord(all_trades, start_balance)

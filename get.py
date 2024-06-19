import json
from discord_webhook import DiscordWebhook, DiscordEmbed


WEBHOOK_URL = 'WEBHOOKAPI LU'


DATA_FILE = 'trading_data.json'

def load_trading_data():
    try:
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            return data.get('trades', [])
    except FileNotFoundError:
        print(f"File '{DATA_FILE}' tidak ditemukan.")
        return []
    except Exception as e:
        print(f"Terjadi kesalahan saat memuat data: {str(e)}")
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
        print("Tidak ada data untuk dikirim ke Discord.")
        return
    
    embed = DiscordEmbed(title="Trading Report", color=0x00ff00) 
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
        print("Data berhasil dikirim ke Discord.")
    else:
        print(f"Terjadi kesalahan: {response.status_code}, {response.text}")



trades = load_trading_data()

coin_pnl_list = get_coin_pnl(trades)

send_coin_pnl_to_discord(coin_pnl_list)


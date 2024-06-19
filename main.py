import sys

def run_bot():
    print("INPUT JOURNAL")
    try:
        import bot
    except ImportError:
        print("Error: bot.py not found or cannot be imported.")

def run_get():
    print("SENDING TO DISCORD")
    try:
        import get
    except ImportError:
        print("Error: get.py not found or cannot be imported.")

if __name__ == "__main__":
    print("Pilih skrip yang ingin dijalankan:")
    print("1. INPUT JOURNAL")
    print("2. GET DATA")
    choice = input("Masukkan pilihan (1/2): ")

    if choice == "1":
        run_bot()
    elif choice == "2":
        run_get()
    else:
        print("Masukan Pilihan Yang Benar.")

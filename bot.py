import os
import time
import requests
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("Falta TELEGRAM_TOKEN")
    exit()

API = f"https://api.telegram.org/bot{TOKEN}"

last_update = 0


def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    data = requests.get(url, timeout=10).json()
    return float(data["price"])


def get_signal():
    price1 = get_btc_price()
    time.sleep(2)
    price2 = get_btc_price()

    change = ((price2 - price1) / price1) * 100

    if change > 0.015:
        signal = "🟢 UP"
    elif change < -0.015:
        signal = "🔴 DOWN"
    else:
        signal = "🟡 ESPERAR"

    return price2, change, signal


def send_message(chat_id, text):
    requests.post(
        f"{API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=10
    )


def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").lower().strip()

    if text in ["/start", "start"]:
        send_message(
            chat_id,
            "🤖 BTC SIGNAL BOT\n\n"
            "Estoy conectado.\n\n"
            "Usa /analizar para analizar BTC.\n"
            "Usa /precio para ver el precio actual."
        )

    elif text in ["/precio", "precio"]:
        try:
            price = get_btc_price()
            send_message(
                chat_id,
                f"₿ BTC\n\nPrecio actual: ${price:,.2f}"
            )
        except Exception:
            send_message(chat_id, "❌ No pude obtener el precio.")

    elif text in ["/analizar", "analizar"]:
        try:
            price, change, signal = get_signal()

            send_message(
                chat_id,
                "📊 ANÁLISIS BTC\n\n"
                f"Precio: ${price:,.2f}\n"
                f"Movimiento: {change:+.3f}%\n\n"
                f"SEÑAL: {signal}\n\n"
                "⚠️ Señal experimental. No garantiza ganancias."
            )

        except Exception:
            send_message(
                chat_id,
                "❌ Error obteniendo datos de BTC."
            )

    else:
        send_message(
            chat_id,
            "🤖 Comandos disponibles:\n\n"
            "/analizar — analizar BTC\n"
            "/precio — precio actual"
        )


def main():
    global last_update

    print("🤖 Bot iniciado...")

    while True:
        try:
            response = requests.get(
                f"{API}/getUpdates",
                params={
                    "offset": last_update + 1,
                    "timeout": 20
                },
                timeout=30
            ).json()

            for update in response.get("result", []):
                last_update = update["update_id"]

                if "message" in update:
                    handle_message(update["message"])

        except Exception as e:
            print("Error:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()

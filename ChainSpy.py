import requests
from datetime import datetime, timedelta
import time

ETHERSCAN_API_KEY = "YourApiKeyHere"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

def get_recent_tokens(minutes_back=60):
    """Получает контракты токенов, созданные за последние N минут"""
    current_time = int(time.time())
    start_time = current_time - (minutes_back * 60)

    response = requests.get(ETHERSCAN_API_URL, params={
        "module": "account",
        "action": "txlistinternal",
        "starttimestamp": start_time,
        "endtimestamp": current_time,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    })

    if response.status_code != 200:
        raise Exception("Ошибка при запросе к Etherscan")

    data = response.json()["result"]
    contracts = [tx["contractAddress"] for tx in data if tx["contractAddress"]]
    return list(set(contracts))

def is_suspicious(token_address):
    """Анализирует токен и возвращает True, если поведение подозрительно"""
    # Пример простой эвристики: мало держателей, все транзакции идут одному адресу
    url = f"{ETHERSCAN_API_URL}?module=token&action=tokenholderlist&contractaddress={token_address}&apikey={ETHERSCAN_API_KEY}"
    r = requests.get(url)
    holders_data = r.json().get("result", [])

    if not holders_data or len(holders_data) < 3:
        return True

    return False

def main():
    print("[🔍] Поиск новых токенов и анализ поведения...")
    tokens = get_recent_tokens(minutes_back=120)

    if not tokens:
        print("Нет новых токенов за последние 2 часа.")
        return

    for token in tokens:
        try:
            if is_suspicious(token):
                print(f"[⚠️ ПОДОЗРИТЕЛЬНЫЙ] {token}")
            else:
                print(f"[✅ ОК] {token}")
        except Exception as e:
            print(f"[Ошибка] {token}: {str(e)}")

if __name__ == "__main__":
    main()

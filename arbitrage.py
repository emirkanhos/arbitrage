import requests
import streamlit as st


def get_binance_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=5"
        response = requests.get(url)
        response.raise_for_status()
        order_book = response.json()
        best_bid_price = float(order_book['bids'][0][0])  # En iyi alış fiyatı
        best_ask_price = float(order_book['asks'][0][0])  # En iyi satış fiyatı
        return best_bid_price, best_ask_price
    except Exception as e:
        st.error(f"Binance fiyat çekme hatası ({symbol}): {e}")
        return None, None


def get_okx_price(symbol):
    try:
        url = f"https://www.okx.com/api/v5/market/books?instId={symbol}&sz=5"
        response = requests.get(url)
        response.raise_for_status()
        order_book = response.json()['data'][0]
        best_bid_price = float(order_book['bids'][0][0])  # En iyi alış fiyatı
        return best_bid_price
    except Exception as e:
        st.error(f"OKX fiyat çekme hatası ({symbol}): {e}")
        return None


def calculate_profit_from_okx_to_binance(okx_usdt_try, binance_fdusd_try_ask, binance_fdusd_usdt_bid, user_try_amount):
    try:
        if okx_usdt_try and binance_fdusd_try_ask and binance_fdusd_usdt_bid:
            usdt_from_try = user_try_amount // okx_usdt_try
            fdusd_from_usdt = usdt_from_try // binance_fdusd_usdt_bid
            try_from_fdusd = fdusd_from_usdt * binance_fdusd_try_ask

            profit_from_user_try = try_from_fdusd - user_try_amount
            profit_ratio = (profit_from_user_try / user_try_amount) * 100

            st.write(f"OKX'te {user_try_amount} TRY ile {usdt_from_try} USDT alındı.")
            st.write(f"Binance'de {usdt_from_try} USDT ile {fdusd_from_usdt} FDUSD alındı.")
            st.write(f"Binance'de {fdusd_from_usdt} FDUSD ile {try_from_fdusd:.2f} TRY elde edildi.")

            return profit_ratio, profit_from_user_try, "OKX -> Binance"
        else:
            st.error("Eksik fiyat bilgisi nedeniyle kar hesaplanamadı.")
            return None, None, None
    except Exception as e:
        st.error(f"Kar hesaplama hatası: {e}")
        return None, None, None


def calculate_profit_from_binance_to_okx(binance_fdusd_try_bid, binance_fdusd_usdt_bid, okx_usdt_try, user_try_amount):
    try:
        if binance_fdusd_try_bid and binance_fdusd_usdt_bid and okx_usdt_try:
            fdusd_from_try = user_try_amount // binance_fdusd_try_bid
            usdt_from_fdusd = fdusd_from_try * binance_fdusd_usdt_bid
            try_from_usdt = usdt_from_fdusd * okx_usdt_try

            profit_from_user_try = try_from_usdt - user_try_amount
            profit_ratio = (profit_from_user_try / user_try_amount) * 100

            st.write(f"Binance'de {user_try_amount} TRY ile {fdusd_from_try} FDUSD alındı.")
            st.write(f"Binance'de {fdusd_from_try} FDUSD ile {usdt_from_fdusd} USDT elde edildi.")
            st.write(f"OKX'te {usdt_from_fdusd} USDT ile {try_from_usdt:.2f} TRY alındı.")

            return profit_ratio, profit_from_user_try, "Binance -> OKX"
        else:
            st.error("Eksik fiyat bilgisi nedeniyle kar hesaplanamadı.")
            return None, None, None
    except Exception as e:
        st.error(f"Kar hesaplama hatası: {e}")
        return None, None, None


st.title("OKX ve Binance Arbitraj Fırsatları")
user_try_amount = st.number_input("İşlem yapmak istediğiniz TRY miktarını girin:", min_value=1, step=1)

if st.button("Hesapla"):
    st.write("Fiyatlar çekiliyor...")

    binance_fdusd_try_bid, binance_fdusd_try_ask = get_binance_price("FDUSDTRY")
    binance_fdusd_usdt_bid, _ = get_binance_price("FDUSDUSDT")
    okx_usdt_try = get_okx_price("USDT-TRY")

    profit_ratio_okx_to_binance, profit_from_user_try_okx_to_binance, route_okx_to_binance = calculate_profit_from_okx_to_binance(
        okx_usdt_try, binance_fdusd_try_ask, binance_fdusd_usdt_bid, user_try_amount)

    profit_ratio_binance_to_okx, profit_from_user_try_binance_to_okx, route_binance_to_okx = calculate_profit_from_binance_to_okx(
        binance_fdusd_try_bid, binance_fdusd_usdt_bid, okx_usdt_try, user_try_amount)

    if profit_ratio_okx_to_binance is not None:
        st.success(f"{route_okx_to_binance}: Tahmini Kar Oranı: {profit_ratio_okx_to_binance:.2f}%")
        st.success(
            f"{user_try_amount} TRY ile işlem yapıldığında tahmini kar: {profit_from_user_try_okx_to_binance:.2f} TRY")

    if profit_ratio_binance_to_okx is not None:
        st.success(f"{route_binance_to_okx}: Tahmini Kar Oranı: {profit_ratio_binance_to_okx:.2f}%")
        st.success(
            f"{user_try_amount} TRY ile işlem yapıldığında tahmini kar: {profit_from_user_try_binance_to_okx:.2f} TRY")
import httpx
import asyncio
import streamlit as st

@st.cache_data(ttl=60)  # Önbellek süresi 60 saniye
async def get_binance_price(symbol):
    """
    Binance'den belirtilen paritenin limit emirle alınacak alış veya satış fiyatını alır.
    """
    try:
        url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=5"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        response.raise_for_status()
        order_book = response.json()
        best_bid_price = float(order_book['bids'][0][0])  # En iyi alış fiyatı
        best_ask_price = float(order_book['asks'][0][0])  # En iyi satış fiyatı
        return best_bid_price, best_ask_price
    except Exception as e:
        st.error(f"Binance fiyat çekme hatası ({symbol}): {e}")
        return None, None

@st.cache_data(ttl=60)  # Önbellek süresi 60 saniye
async def get_okx_price(symbol):
    """
    OKX'ten belirtilen paritenin limit emirle alınacak alış fiyatını alır.
    """
    try:
        url = f"https://www.okx.com/api/v5/market/books?instId={symbol}&sz=5"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        response.raise_for_status()
        order_book = response.json()['data'][0]
        best_bid_price = float(order_book['bids'][0][0])  # En iyi alış fiyatı
        return best_bid_price
    except Exception as e:
        st.error(f"OKX fiyat çekme hatası ({symbol}): {e}")
        return None

async def calculate_prices(user_try_amount):
    """
    Bu fonksiyon tüm fiyatları asenkron olarak çeker.
    """
    try:
        binance_fdusd_try_bid, binance_fdusd_try_ask = await get_binance_price("FDUSDTRY")
        binance_fdusd_usdt_bid, _ = await get_binance_price("FDUSDUSDT")
        okx_usdt_try = await get_okx_price("USDT-TRY")

        if not all([binance_fdusd_try_bid, binance_fdusd_try_ask, binance_fdusd_usdt_bid, okx_usdt_try]):
            st.error("Bazı fiyatlar alınamadı, lütfen daha sonra tekrar deneyin.")
            return None

        st.write(f"Binance FDUSD/TRY Alış: {binance_fdusd_try_bid}, Satış: {binance_fdusd_try_ask}")
        st.write(f"Binance FDUSD/USDT Alış: {binance_fdusd_usdt_bid}")
        st.write(f"OKX USDT/TRY Alış: {okx_usdt_try}")

    except Exception as e:
        st.error(f"Fiyat hesaplama hatası: {e}")

async def main():
    user_try_amount = st.number_input("İşlem yapmak istediğiniz TRY miktarını girin:", min_value=1, step=1)
    if st.button("Fiyatları Getir"):
        st.write("Fiyatlar çekiliyor...")
        await calculate_prices(user_try_amount)

if __name__ == "__main__":
    asyncio.run(main())

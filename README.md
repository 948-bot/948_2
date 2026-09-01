# XAUUSD AI DERIV BOT - Super Premium

Bot sinyal trading XAUUSD berbasis multi-timeframe (H4, H1, M30, M15) dengan indikator teknikal lengkap.

## Fitur
- Analisis tren besar menggunakan EMA, MACD, ADX, Ichimoku
- Deteksi pola candlestick (engulfing, pin bar, inside bar)
- Sinyal hanya dengan skor >= 80 dan multi-konfirmasi
- Filter sesi pasar London & New York
- Filter volatilitas minimum (ATR)
- Manajemen risiko 2% per trade
- Anti-spam persisten
- Notifikasi Telegram detail

## Cara Menjalankan
1. Clone folder ini.
2. Install dependencies: `pip install -r requirements.txt`
3. Isi file `.env` dengan token bot Telegram dan chat ID Anda.
4. Jalankan: `python main.py`

## Catatan
- Bot hanya mengirim sinyal (tidak eksekusi otomatis).
- Selalu uji di akun demo terlebih dahulu.
- Tidak ada jaminan profit.

# Weather API Server

本程式使用 Flask 建立一個 REST API，提供即時氣象資料給 ESP32。

## 使用方式
1. 設定環境變數 `CWB_API_KEY` 為你的中央氣象局 API Key
2. 執行伺服器：
```bash
python server.py

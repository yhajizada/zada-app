import time
import threading
import requests
import webview
import uvicorn

def start_server():
    # log_level="critical" – terminalı səliqəli saxlayır
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="critical")

if __name__ == "__main__":
    # 1. Serveri ayrı pəncərədə/axında başladırıq
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 2. Serverin işə düşməsini gözləyirik (127.0.0.1:8000 cavab verənə qədər)
    print("Server başladılır, gözləyin...")
    while True:
        try:
            response = requests.get("http://127.0.0.1:8000/docs") # FastAPI-nin avtomatik sənəd səhifəsini yoxlayırıq
            if response.status_code == 200:
                break
        except connection_error:
            pass
        time.sleep(0.5) # Yarım saniyə gözləyib yenidən yoxlayır

    # 3. Server hazır olandan sonra proqram pəncərəsini açırıq
    webview.create_window(
        "ZADA Enterprise Ultimate Pro", 
        "http://127.0.0.1:8000", 
        width=1500, 
        height=900
    )
    webview.start()
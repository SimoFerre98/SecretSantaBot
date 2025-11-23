import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = "webapp"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    # Assicurati che la directory esista
    if not os.path.exists(DIRECTORY):
        print(f"Errore: La cartella '{DIRECTORY}' non esiste.")
        exit(1)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🎅 Mini App Server avviato su http://localhost:{PORT}")
        print("Premi Ctrl+C per fermarlo.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server fermato.")

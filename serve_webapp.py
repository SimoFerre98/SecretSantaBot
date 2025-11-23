import http.server
import socketserver
import os
import json
import sys

# Aggiungi src al path per importare i moduli
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from group_management import join_group

PORT = 8000
DIRECTORY = "webapp"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/groups":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            # Leggi il file groups.json dalla root (una cartella sopra webapp)
            groups_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "groups", "groups.json")
            if os.path.exists(groups_path):
                with open(groups_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"{}")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/join":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            group_id = data.get("group_id")
            user_name = data.get("user_name")
            access_code = data.get("access_code")
            
            success, msg = join_group(group_id, user_name, access_code=access_code)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": msg}).encode())
        else:
            self.send_error(404)

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

#!/usr/bin/env python3
"""
SmartLeakPro - Serveur HTTP simple pour démonstration
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime
import uuid
import os

# Données en mémoire
clients_db = []
interventions_db = []

class SmartLeakHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "message": "SmartLeakPro API - Version Démo",
                "status": "running",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "clients": "/api/clients",
                    "interventions": "/api/interventions",
                    "demo": "/demo",
                    "init": "/api/demo/init"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "clients_count": len(clients_db),
                "interventions_count": len(interventions_db)
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == '/api/clients':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(clients_db, indent=2).encode())
            
        elif self.path == '/api/interventions':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(interventions_db, indent=2).encode())
            
        elif self.path == '/api/demo/init':
            # Initialiser les données de démo
            global clients_db, interventions_db
            
            clients_db = [
                {
                    "id": str(uuid.uuid4()),
                    "nom": "Client Démo 1",
                    "email": "client1@demo.com",
                    "telephone": "0123456789",
                    "adresse": "123 Rue Démo, 75001 Paris",
                    "statut": "actif",
                    "date_creation": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "nom": "Client Démo 2",
                    "email": "client2@demo.com",
                    "telephone": "0987654321",
                    "adresse": "456 Avenue Test, 69000 Lyon",
                    "statut": "actif",
                    "date_creation": datetime.utcnow().isoformat()
                }
            ]
            
            interventions_db = [
                {
                    "id": str(uuid.uuid4()),
                    "client_id": clients_db[0]["id"],
                    "date_intervention": datetime.utcnow().isoformat(),
                    "type_intervention": "inspection",
                    "statut": "planifie",
                    "lieu": "123 Rue Démo, 75001 Paris",
                    "description": "Inspection de routine",
                    "date_creation": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "client_id": clients_db[1]["id"],
                    "date_intervention": datetime.utcnow().isoformat(),
                    "type_intervention": "detection",
                    "statut": "en_cours",
                    "lieu": "456 Avenue Test, 69000 Lyon",
                    "description": "Détection de fuite urgente",
                    "date_creation": datetime.utcnow().isoformat()
                }
            ]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "message": "Données de démonstration initialisées avec succès",
                "clients": len(clients_db),
                "interventions": len(interventions_db)
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == '/demo':
            # Servir le fichier de démo
            demo_file = 'frontend/complete_demo.html'
            if os.path.exists(demo_file):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(demo_file, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode())
            else:
                self.send_error(404, "Fichier de démo non trouvé")
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/clients':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            client_data = json.loads(post_data.decode('utf-8'))
            
            new_client = {
                "id": str(uuid.uuid4()),
                "nom": client_data.get("nom", ""),
                "email": client_data.get("email", ""),
                "telephone": client_data.get("telephone", ""),
                "adresse": client_data.get("adresse", ""),
                "statut": client_data.get("statut", "actif"),
                "date_creation": datetime.utcnow().isoformat()
            }
            
            clients_db.append(new_client)
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(new_client, indent=2).encode())
            
        elif self.path == '/api/interventions':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            intervention_data = json.loads(post_data.decode('utf-8'))
            
            new_intervention = {
                "id": str(uuid.uuid4()),
                "client_id": intervention_data.get("client_id", ""),
                "date_intervention": intervention_data.get("date_intervention", datetime.utcnow().isoformat()),
                "type_intervention": intervention_data.get("type_intervention", ""),
                "statut": intervention_data.get("statut", "planifie"),
                "lieu": intervention_data.get("lieu", ""),
                "description": intervention_data.get("description", ""),
                "date_creation": datetime.utcnow().isoformat()
            }
            
            interventions_db.append(new_intervention)
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(new_intervention, indent=2).encode())
        else:
            self.send_error(404, "Endpoint non trouvé")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    PORT = 8000
    
    print("🚀 Démarrage de SmartLeakPro...")
    print("📡 Backend: http://localhost:8000")
    print("🌐 Frontend: http://localhost:8000/demo")
    print("❤️  Health: http://localhost:8000/health")
    print("=" * 50)
    
    with socketserver.TCPServer(("", PORT), SmartLeakHandler) as httpd:
        print(f"✅ Serveur démarré sur le port {PORT}")
        print("Appuyez sur Ctrl+C pour arrêter")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
            httpd.shutdown()

if __name__ == "__main__":
    run_server()

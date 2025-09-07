from django.shortcuts import render
from django.http import HttpResponse

def report_list_simple(request):
    """Simple test view for reports"""
    return HttpResponse("""
    <html>
    <head>
        <title>Rapports d'Intervention - SmartLeakPro</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>🌊 Rapports d'Intervention</h1>
            <p>Module de rapports d'intervention en cours de développement.</p>
            <div class="alert alert-info">
                <h4>Fonctionnalités disponibles :</h4>
                <ul>
                    <li>Création de rapports dynamiques</li>
                    <li>Gestion des médias (photos, vidéos, audio)</li>
                    <li>Signatures électroniques</li>
                    <li>Export multi-format (PDF, Word, HTML)</li>
                    <li>Templates personnalisables</li>
                </ul>
            </div>
            <a href="/" class="btn btn-primary">Retour à l'accueil</a>
        </div>
    </body>
    </html>
    """)

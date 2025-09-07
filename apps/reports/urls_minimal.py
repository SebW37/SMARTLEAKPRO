from django.urls import path
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("""
    <html>
    <head>
        <title>Rapports d'Intervention - Test</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>🌊 Rapports d'Intervention - Test</h1>
            <p>Cette page fonctionne ! Le module de rapports est en cours de développement.</p>
            <div class="alert alert-success">
                <h4>✅ Module de rapports chargé avec succès</h4>
                <p>Le système de rapports d'intervention est maintenant opérationnel.</p>
            </div>
            <a href="/" class="btn btn-primary">Retour à l'accueil</a>
        </div>
    </body>
    </html>
    """)

urlpatterns = [
    path('', test_view, name='reports_test'),
]

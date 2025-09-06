#!/bin/bash

# SmartLeakPro Migration Script
# This script runs Django migrations

set -e

echo "🗄️ Running SmartLeakPro migrations..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Load environment variables
source .env

echo "📦 Starting services..."
docker-compose up -d db redis

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🔄 Running migrations..."
docker-compose exec web python manage.py migrate

echo "👤 Creating superuser..."
docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@smartleakpro.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

echo "📊 Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

echo "✅ Migrations completed successfully!"
echo ""
echo "🌐 Application URLs:"
echo "   API: http://localhost:8000/api/"
echo "   Admin: http://localhost:8000/admin/"
echo ""
echo "👤 Admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"

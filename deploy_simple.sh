#!/bin/bash

echo "�� Starting SmartLeakPro deployment..."

# Navigate to project directory
cd /home/SMARTLEAKPRO

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Activate virtual environment
echo "�� Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements_simple.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage_simple.py migrate

# Collect static files
echo "📊 Collecting static files..."
python manage_simple.py collectstatic --noinput

# Restart services (only if they exist)
echo "🔄 Restarting services..."
systemctl restart nginx 2>/dev/null || echo "Nginx restart failed or not found"
systemctl restart gunicorn 2>/dev/null || echo "Gunicorn service not found"

# Try to restart any Python processes
pkill -f "python.*manage_simple.py" 2>/dev/null || echo "No Django processes found to restart"

echo "✅ Deployment completed successfully!"

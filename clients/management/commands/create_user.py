"""
Management command to create users easily.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a user easily'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username')
        parser.add_argument('--email', type=str, help='Email (optional)')
        parser.add_argument('--first_name', type=str, help='First name (optional)')
        parser.add_argument('--last_name', type=str, help='Last name (optional)')
        parser.add_argument('--password', type=str, default='password123', help='Password (default: password123)')

    def handle(self, *args, **options):
        username = options['username']
        if not username:
            self.stdout.write(self.style.ERROR('Username is required'))
            return

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            return

        # Create user
        user = User.objects.create_user(
            username=username,
            email=options.get('email', ''),
            first_name=options.get('first_name', ''),
            last_name=options.get('last_name', ''),
            password=options['password']
        )

        self.stdout.write(self.style.SUCCESS(f'User {username} created successfully!'))
        self.stdout.write(f'Password: {options["password"]}')

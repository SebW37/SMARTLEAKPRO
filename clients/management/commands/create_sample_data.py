"""
Management command to create sample data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clients.models import Client, ClientSite


class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create a test user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': True,
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user'))

        # Create sample clients
        clients_data = [
            {
                'name': 'Entreprise ABC',
                'client_type': 'company',
                'email': 'contact@abc.com',
                'phone': '01 23 45 67 89',
                'address': '123 Rue de la Paix',
                'city': 'Paris',
                'postal_code': '75001',
                'notes': 'Client important pour la détection de fuites',
            },
            {
                'name': 'M. Dupont',
                'client_type': 'individual',
                'email': 'dupont@email.com',
                'phone': '06 12 34 56 78',
                'address': '456 Avenue des Champs',
                'city': 'Lyon',
                'postal_code': '69001',
                'notes': 'Particulier avec plusieurs propriétés',
            },
            {
                'name': 'Mairie de Marseille',
                'client_type': 'public',
                'email': 'services@marseille.fr',
                'phone': '04 91 00 00 00',
                'address': '789 Place de la Mairie',
                'city': 'Marseille',
                'postal_code': '13001',
                'notes': 'Collectivité territoriale - bâtiments publics',
            },
        ]

        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                name=client_data['name'],
                defaults={
                    **client_data,
                    'created_by': user,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created client: {client.name}'))
                
                # Create a site for each client
                site = ClientSite.objects.create(
                    client=client,
                    name=f"Site principal - {client.name}",
                    address=client.address,
                    city=client.city,
                    postal_code=client.postal_code,
                    country=client.country,
                    contact_name=client.name,
                    contact_email=client.email,
                    contact_phone=client.phone,
                )
                self.stdout.write(self.style.SUCCESS(f'Created site: {site.name}'))

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

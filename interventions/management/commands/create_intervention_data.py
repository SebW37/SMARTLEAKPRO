"""
Management command to create sample intervention data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from clients.models import Client, ClientSite
from interventions.models import LeakType, Equipment, Intervention, TechnicianAvailability


class Command(BaseCommand):
    help = 'Create sample intervention data for testing'

    def handle(self, *args, **options):
        # Créer des types de fuites
        leak_types_data = [
            {'name': 'Fuite eau chaude', 'description': 'Fuite dans le circuit d\'eau chaude', 'severity_level': 3},
            {'name': 'Fuite eau froide', 'description': 'Fuite dans le circuit d\'eau froide', 'severity_level': 2},
            {'name': 'Fuite gaz', 'description': 'Fuite de gaz naturel ou propane', 'severity_level': 4},
            {'name': 'Fuite chauffage', 'description': 'Fuite dans le circuit de chauffage', 'severity_level': 3},
            {'name': 'Fuite évacuation', 'description': 'Fuite dans les canalisations d\'évacuation', 'severity_level': 1},
        ]

        for leak_data in leak_types_data:
            leak_type, created = LeakType.objects.get_or_create(
                name=leak_data['name'],
                defaults=leak_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created leak type: {leak_type.name}'))

        # Créer des équipements
        equipment_data = [
            {'name': 'Détecteur de fuites ultrasons', 'category': 'detection', 'model': 'US-2000', 'available': True},
            {'name': 'Caméra thermique', 'category': 'detection', 'model': 'FLIR-E4', 'available': True},
            {'name': 'Endoscope', 'category': 'detection', 'model': 'ENDO-50', 'available': True},
            {'name': 'Manomètre digital', 'category': 'measurement', 'model': 'MANO-DIGI', 'available': True},
            {'name': 'Détecteur de gaz', 'category': 'safety', 'model': 'GAS-ALERT', 'available': True},
            {'name': 'Appareil photo', 'category': 'documentation', 'model': 'CANON-EOS', 'available': True},
        ]

        for equip_data in equipment_data:
            equipment, created = Equipment.objects.get_or_create(
                name=equip_data['name'],
                defaults=equip_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created equipment: {equipment.name}'))

        # Créer des techniciens
        technicians_data = [
            {'username': 'jean.dupont', 'email': 'jean.dupont@smartleakpro.com', 'first_name': 'Jean', 'last_name': 'Dupont'},
            {'username': 'marie.martin', 'email': 'marie.martin@smartleakpro.com', 'first_name': 'Marie', 'last_name': 'Martin'},
            {'username': 'pierre.durand', 'email': 'pierre.durand@smartleakpro.com', 'first_name': 'Pierre', 'last_name': 'Durand'},
        ]

        technicians = []
        for tech_data in technicians_data:
            technician, created = User.objects.get_or_create(
                username=tech_data['username'],
                defaults={
                    **tech_data,
                    'is_staff': True,
                }
            )
            if created:
                technician.set_password('password123')
                technician.save()
                self.stdout.write(self.style.SUCCESS(f'Created technician: {technician.get_full_name()}'))
            technicians.append(technician)

        # Créer des disponibilités pour les techniciens
        today = timezone.now().date()
        for i in range(7):  # 7 jours
            date = today + timedelta(days=i)
            for technician in technicians:
                TechnicianAvailability.objects.get_or_create(
                    technician=technician,
                    date=date,
                    start_time='08:00',
                    end_time='18:00',
                    defaults={'is_available': True}
                )

        # Récupérer les clients existants
        clients = Client.objects.all()
        if not clients.exists():
            self.stdout.write(self.style.ERROR('No clients found. Please run create_sample_data first.'))
            return

        # Créer des interventions
        interventions_data = [
            {
                'title': 'Fuite eau chaude - Salle de bain',
                'description': 'Fuite importante dans la salle de bain, eau chaude qui fuit derrière le carrelage',
                'priority': 'high',
                'status': 'scheduled',
                'scheduled_date': timezone.now() + timedelta(days=1, hours=9),
                'estimated_duration': timedelta(hours=2),
            },
            {
                'title': 'Fuite gaz - Cuisine',
                'description': 'Suspicion de fuite de gaz dans la cuisine, odeur détectée',
                'priority': 'critical',
                'status': 'scheduled',
                'scheduled_date': timezone.now() + timedelta(hours=2),
                'estimated_duration': timedelta(hours=1, minutes=30),
            },
            {
                'title': 'Fuite chauffage - Salon',
                'description': 'Radiateur qui fuit dans le salon, tache d\'eau au sol',
                'priority': 'medium',
                'status': 'in_progress',
                'scheduled_date': timezone.now() - timedelta(hours=1),
                'estimated_duration': timedelta(hours=3),
                'actual_start_time': timezone.now() - timedelta(hours=1),
            },
            {
                'title': 'Fuite évacuation - WC',
                'description': 'Fuite dans les canalisations d\'évacuation des WC',
                'priority': 'low',
                'status': 'completed',
                'scheduled_date': timezone.now() - timedelta(days=1),
                'estimated_duration': timedelta(hours=1),
                'actual_start_time': timezone.now() - timedelta(days=1, hours=10),
                'actual_end_time': timezone.now() - timedelta(days=1, hours=11),
                'findings': 'Fuite localisée au niveau du joint de raccordement',
                'recommendations': 'Remplacement du joint recommandé',
            },
        ]

        for i, interv_data in enumerate(interventions_data):
            client = clients[i % len(clients)]
            site = client.sites.first()
            if not site:
                continue

            intervention = Intervention.objects.create(
                client=client,
                site=site,
                technician=technicians[i % len(technicians)],
                created_by=User.objects.filter(is_superuser=True).first(),
                **interv_data
            )

            # Ajouter des types de fuites
            if 'eau chaude' in interv_data['title'].lower():
                leak_type = LeakType.objects.get(name='Fuite eau chaude')
                intervention.leak_types.add(leak_type)
            elif 'gaz' in interv_data['title'].lower():
                leak_type = LeakType.objects.get(name='Fuite gaz')
                intervention.leak_types.add(leak_type)
            elif 'chauffage' in interv_data['title'].lower():
                leak_type = LeakType.objects.get(name='Fuite chauffage')
                intervention.leak_types.add(leak_type)
            elif 'évacuation' in interv_data['title'].lower():
                leak_type = LeakType.objects.get(name='Fuite évacuation')
                intervention.leak_types.add(leak_type)

            # Ajouter des équipements
            equipment = Equipment.objects.filter(available=True)[:3]
            intervention.equipment_needed.set(equipment)

            self.stdout.write(self.style.SUCCESS(f'Created intervention: {intervention.intervention_id}'))

        self.stdout.write(self.style.SUCCESS('Sample intervention data created successfully!'))

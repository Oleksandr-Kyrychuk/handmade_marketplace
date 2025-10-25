import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from pathlib import Path

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with real users from JSON file'

    def handle(self, *args, **kwargs):
        json_path = Path(__file__).resolve().parent / 'users_seed.json'
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f'JSON file not found: {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            users_data = json.load(f)

        created_count = 0
        for data in users_data:
            if not User.objects.filter(email=data['email']).exists():
                user = User.objects.create_user(
                    email=data['email'],
                    username=data['username'],
                    surname=data['surname'],
                    password=data['password'],
                    roles=data.get('roles', ['user']),
                    is_verified=data.get('is_verified', True),
                    verification_token_created_at=now() if not data.get('is_verified', True) else None
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.email} (ID: {user.id})'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} users from JSON.'))

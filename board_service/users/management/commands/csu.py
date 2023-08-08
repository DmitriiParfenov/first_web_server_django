from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            email='admin@localhost.com',
            first_name='admin',
            last_name='adminov',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

        user.set_password('Basketball123')
        user.save()
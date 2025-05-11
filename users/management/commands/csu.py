from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(phone='+79998887766')
        user.set_password('1111')
        user.username = 'Admin'
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

from django.core.management import BaseCommand
from users.models import User
import django.db.utils


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            user, created = User.objects.get_or_create(phone='+79998887766')
            if created:
                user.set_password('1111')
                user.username = 'Admin'
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                user.save()
                print("Пользователь успешно создан.")
            else:
                print("Пользователь с этим номером уже существует.")
        except django.db.utils.IntegrityError:
            print("Ошибка при создании пользователя.")

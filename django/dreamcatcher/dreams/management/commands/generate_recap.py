from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.apps import apps
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate or update monthly recaps for all users starting from June 2024'

    def handle(self, *args, **kwargs):
        Recap = apps.get_model('dreams', 'MonthlyRecap')
        User = apps.get_model('auth', 'User')

        start_month = now().date().replace(year=2024, month=6, day=1)


        current_month = now().date().replace(day=1)


        users = User.objects.all()

        while start_month <= current_month:
            for user in users:
                recap, created = Recap.objects.get_or_create(user=user, month=start_month)
                if created:
                    recap.generate_recap()
                    recap.save()
                    self.stdout.write(self.style.SUCCESS(f"Generated recap for {user.username} ({start_month.strftime('%B %Y')})"))
                else:
                    recap.delete()
                    recap.generate_recap()
                    recap.save()
                    self.stdout.write(self.style.SUCCESS(f"Update recap for {user.username} ({start_month.strftime('%B %Y')})"))

            next_month = start_month + timedelta(days=32)
            start_month = next_month.replace(day=1)

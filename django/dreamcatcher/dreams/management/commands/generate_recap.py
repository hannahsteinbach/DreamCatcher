from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.apps import apps
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate or update monthly recaps for all users starting from June 2024'

    def handle(self, *args, **kwargs):
        # Get the Recap and User models from the apps registry
        Recap = apps.get_model('dreams', 'MonthlyRecap')
        User = apps.get_model('auth', 'User')  # Assuming User model is the default Django User model

        start_month = now().date().replace(year=2024, month=6, day=1)


        current_month = now().date().replace(day=1)


        users = User.objects.all()  # Get all users

        while start_month <= current_month:
            for user in users:
                recap, created = Recap.objects.get_or_create(user=user, month=start_month)
                if created:
                    recap.generate_recap()
                    recap.save()  # Save the recap
                    self.stdout.write(self.style.SUCCESS(f"Generated recap for {user.username} ({start_month.strftime('%B %Y')})"))
                else:
                    recap.delete()
                    recap.generate_recap()
                    recap.save()  # Save the recap
                    self.stdout.write(self.style.SUCCESS(f"Updated recap for {user.username} ({start_month.strftime('%B %Y')})"))

            # Move to the next month
            next_month = start_month + timedelta(days=32)
            start_month = next_month.replace(day=1)

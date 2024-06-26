import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamcatcher.settings')
django.setup()

from django.contrib.auth.models import User
from dreams.models import Dream

# Define users we want to remove
remove_users = {'vickie', 'david', 'samantha'}

# Iterate over all users in remove_users
for username in remove_users:
    try:
        user = User.objects.get(username=username)

        # Delete associated dreams
        dreams = Dream.objects.filter(user=user)
        dreams.delete()

        # Now delete the user
        user.delete()
        print(f"User {username} was successfully removed")

    except User.DoesNotExist:
        print(f"The user {username} you want to remove from the database does not exist")

    except Exception as e:
        print(f"Error occurred while deleting {username}: {str(e)}")
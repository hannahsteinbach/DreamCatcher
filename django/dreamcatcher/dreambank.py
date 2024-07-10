import os
import django
import pandas as pd
from datetime import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamcatcher.settings')
django.setup()

from django.contrib.auth.models import User
from dreams.models import Dream


df = pd.read_parquet("hf://datasets/DReAMy-lib/DreamBank-dreams-en/data/train-00000-of-00001-24937aef854be1c9.parquet")

# Users to include
included_users = {'vickie'}

#included_users = {'vickie', 'david', 'samantha', 'bosnak', 'angie', 'dahlia', 'lawrence', 'ed', 'melora', 'alta',
#                  'toby'}

# Filter DataFrame to include only the specified users
filtered_df = df[df['series'].isin(included_users)]

# Define a default password
default_password = 'defaultpassword123'

# Iterate through each row in the filtered DataFrame
for index, row in filtered_df.iterrows():
    username = row['series']
    dream_content = row['dreams']

    # Ensure user exists, if not create one
    user, created = User.objects.get_or_create(username=username)

    if created:
        # Set a default password for new users
        user.set_password(default_password)
        user.save()

    # Create a random date for the dream
    start_date = datetime(1970, 1, 1)
    random_timestamp = random.randint(int(start_date.timestamp()), int(datetime.now().timestamp()))
    random_date = datetime.fromtimestamp(random_timestamp)

    # Create Dream object
    dream = Dream(
        user=user,
        date=random_date,
        content=dream_content,
    )
    dream.save()

print("Data has been successfully added to the database.")

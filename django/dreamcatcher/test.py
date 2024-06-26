import dreamy

import pandas as pd

# Your report
report = """Fernando and I were at my parents' home in the office when we noticed a fly
 on the floor. It was making very strange noises, we went closer and then it seemed like it was burning up inside or 
 exploding. Suddenly it went bang and exploded, spraying liquid everywhere. only then did i realize that the liquid was
  really hot, like lava, and i felt a thick blister as big as my hand through my pants. fernando was hardly hurt because 
  i pushed him out of the way"""

# Create a DataFrame
reports = [report]

sentiment = "SA"
persons = "NER"
batch_size = 16
device = "cpu"

sentiment_lookup = {"AN": "Anger",
                   "AP": "Apprehension",
                   "SD": "Sadness",
                   "CO": "Confusion",
                   "HA": "Happiness"}


SA_predictions = dreamy.annotate_reports(
    reports,
    task=sentiment,
    device=device,
    batch_size=batch_size,
)

NER_predictions = dreamy.annotate_reports(
    reports,
    task=persons,
    device=device,
    batch_size=batch_size,
)

max = 0
for sentiment in SA_predictions[0]:
    if sentiment['score'] > max:
        max = sentiment['score']
        highest_label = sentiment['label']


print(SA_predictions[0])
print(NER_predictions)


NER_predictions = NER_predictions.strip("[]").strip("'").split(";")

print(NER_predictions)


#print("Sentiment:", sentiment_lookup[highest_label])
print("Person: ", NER_predictions[0])
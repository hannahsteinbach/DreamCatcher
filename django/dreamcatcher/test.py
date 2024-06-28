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

persons = "NER"
batch_size = 16
device = "cpu"

NER_predictions = dreamy.annotate_reports(
    reports,
    task=persons,
    device=device,
    batch_size=batch_size,
)

print(NER_predictions)


NER_predictions = NER_predictions[0].split(";")
NER_predictions.remove('')

#print("Sentiment:", sentiment_lookup[highest_label])
print("Person: ", NER_predictions)
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

with open('gold.json', 'r') as f:
    gold_data = json.load(f)

filename = 'multishot3_llama.json'
with open(filename, 'r') as f:
    predicted_data = json.load(f)

gold_labels = []
predicted_labels = []
dream_ids = []

# Extract gold labels and dream IDs from gold.json
for dream in gold_data:
    dream_id = dream['dream_id']
    gold_labels.append(dream['emotion'])
    dream_ids.append(dream_id)

# Extract predicted labels from dreamy.json assuming the order matches
predicted_labels = [dream['emotion'] for dream in predicted_data]

# Ensure both lists are the same length before proceeding
if len(gold_labels) != len(predicted_labels):
    raise ValueError("The number of dreams in gold.json and dreamy.json do not match!")

# Calculate overall accuracy
overall_accuracy = accuracy_score(gold_labels, predicted_labels)

# Per-class metrics
class_metrics = {}
classes = ["apprehension", "anger", "happiness", "", "confusion", "sadness"]

for cls in classes:
    binary_gold_labels = [1 if label == cls else 0 for label in gold_labels]
    binary_predicted_labels = [1 if label == cls else 0 for label in predicted_labels]

    precision = precision_score(binary_gold_labels, binary_predicted_labels, zero_division=0)
    recall = recall_score(binary_gold_labels, binary_predicted_labels, zero_division=0)
    f1 = f1_score(binary_gold_labels, binary_predicted_labels, zero_division=0)

    class_accuracy = accuracy_score(binary_gold_labels, binary_predicted_labels)

    class_metrics[cls] = {
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1,
        'Accuracy': class_accuracy
    }

# Track correct and incorrect predictions
correctly_predicted = []
wrongly_predicted = []

correct_count = 0
incorrect_count = 0

# Compare gold labels and predicted labels by index
for i, (gold, pred) in enumerate(zip(gold_labels, predicted_labels)):
    dream_id = dream_ids[i]
    if gold == pred:
        correctly_predicted.append({
            'Dream ID': dream_id,
            'Gold Label': gold,
            'Predicted Label': pred
        })
        correct_count += 1
    else:
        wrongly_predicted.append({
            'Dream ID': dream_id,
            'Gold Label': gold,
            'Predicted Label': pred
        })
        incorrect_count += 1

# Prepare evaluation results
evaluation_results = {
    'Overall Accuracy': overall_accuracy,
    'Class Metrics': class_metrics,
    'Correct Predictions': {
        'Count': correct_count,
        'Details': correctly_predicted
    },
    'Wrong Predictions': {
        'Count': incorrect_count,
        'Details': wrongly_predicted
    }
}

# Save the evaluation results to a JSON file
json_file = f"evaluation_emotions_{filename}"
with open(json_file, 'w') as f:
    json.dump(evaluation_results, f, indent=4)

print(f"Evaluation results saved to {json_file}.")

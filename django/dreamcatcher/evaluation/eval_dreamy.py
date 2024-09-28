import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

with open('gold.json', 'r') as f:
    gold_data = json.load(f)

with open('dreamy.json', 'r') as f:
    predicted_data = json.load(f)

gold_labels = []
predicted_labels = []
dream_ids = []

for dream in gold_data:
    dream_id = dream['dream_id']
    gold_labels.append(dream['emotion'])

    predicted_dream = next((d for d in predicted_data if d['dream_id'] == dream_id), None)
    if predicted_dream:
        predicted_labels.append(predicted_dream['emotion'])
    else:
        predicted_labels.append(None)

    dream_ids.append(dream_id)

overall_accuracy = accuracy_score(gold_labels, predicted_labels)

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

correctly_predicted = []
wrongly_predicted = []

correct_count = 0
incorrect_count = 0

for id, gold, pred in zip(dream_ids, gold_labels, predicted_labels):
    if gold == pred:
        correctly_predicted.append({
            'Dream ID': id,
            'Gold Label': gold,
            'Predicted Label': pred
        })
        correct_count += 1
    else:
        wrongly_predicted.append({
            'Dream ID': id,
            'Gold Label': gold,
            'Predicted Label': pred
        })
        incorrect_count += 1

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

json_file = 'evaluation_dreamy.json'
with open(json_file, 'w') as f:
    json.dump(evaluation_results, f, indent=4)

print(f"Evaluation results saved to {json_file}.")

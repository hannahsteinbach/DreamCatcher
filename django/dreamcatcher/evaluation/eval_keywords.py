import json
import re

# Load the gold and prediction files
with open('gold.json', 'r') as f:
    gold_data = json.load(f)

filename = 'keybert.json'
with open(filename, 'r') as f:
    predicted_data = json.load(f)

# Initialize storage for detailed results and counts
results = {
    'Keywords': {'TP': 0, 'FP': 0, 'FN': 0, 'Details': []}
}

# Function to ignore case and periods in names
def ignore_case_and_periods(name):
    return name.lower().replace('.', '')

# Function to compare two lists while ignoring case and periods
def compare_lists(gold_list, predicted_list):
    normalized_gold = [ignore_case_and_periods(item) for item in gold_list]
    normalized_pred = [ignore_case_and_periods(item) for item in predicted_list]

    gold_set = set(normalized_gold)
    pred_set = set(normalized_pred)

    tp = gold_set & pred_set  # True Positives
    fp = pred_set - gold_set   # False Positives
    fn = gold_set - pred_set    # False Negatives

    return {
        'TP': list(tp),
        'FP': list(fp),
        'FN': list(fn),
        'TP_count': len(tp),
        'FP_count': len(fp),
        'FN_count': len(fn)
    }


def compare_keywords(gold_keywords, predicted_keywords):
    return compare_lists(gold_keywords, predicted_keywords)

# Iterate through each dream and compare characters, locations, and keywords
for gold_dream, pred_dream in zip(gold_data, predicted_data):
    dream_id = gold_dream['dream_id']  # Assuming dream IDs are present in both
    # Compare keywords
    gold_keywords = gold_dream.get('keywords', [])  # Assuming keywords are present in gold
    pred_keywords = pred_dream.get('keywords', [])  # Assuming keywords are present in predicted

    keyword_comparison = compare_keywords(gold_keywords, pred_keywords)
    results['Keywords']['TP'] += keyword_comparison['TP_count']
    results['Keywords']['FP'] += keyword_comparison['FP_count']
    results['Keywords']['FN'] += keyword_comparison['FN_count']
    results['Keywords']['Details'].append({
        'Dream ID': dream_id,
        'True Positives': keyword_comparison['TP'],
        'False Positives': keyword_comparison['FP'],
        'False Negatives': keyword_comparison['FN'],
        'TP_count': keyword_comparison['TP_count'],
        'FP_count': keyword_comparison['FP_count'],
        'FN_count': keyword_comparison['FN_count']
    })

# Save the results to a JSON file
json_file = f"evaluation_keywords_{filename}"
with open(json_file, 'w') as f:
    json.dump(results, f, indent=4)

print(f"Evaluation results saved to {json_file}.")

import json
import re

with open('gold.json', 'r') as f:
    gold_data = json.load(f)

filename = 'zeroshot_llama.json'
with open(filename, 'r') as f:
    predicted_data = json.load(f)

results = {
    'Characters': {'TP': 0, 'FP': 0, 'FN': 0, 'Details': []},
    'Locations': {'TP': 0, 'FP': 0, 'FN': 0, 'Details': []}
}

# ignore periods and case
def ignore_case_and_periods(name):
    return name.lower().replace('.', '')

# ignore periods and case AND accept articles in front
def normalize_name(name):
    # Remove periods and convert to lowercase
    name = ignore_case_and_periods(name)
    # Remove articles ('the', 'a') at the beginning of the name
    return re.sub(r'^(the|a)\s+', '', name)


def compare_lists(gold_list, predicted_list):
    # Normalize both lists
    normalized_gold = [normalize_name(item) for item in gold_list] #change here if you want to be stricter/leaner
    normalized_pred = [normalize_name(item) for item in predicted_list]

    gold_set = set(normalized_gold)
    pred_set = set(normalized_pred)

    tp = gold_set & pred_set  # True Positives: in both gold and predicted
    fp = pred_set - gold_set  # False Positives: in predicted but not in gold
    fn = gold_set - pred_set  # False Negatives: in gold but not in predicted

    return {
        'TP': list(tp),
        'FP': list(fp),
        'FN': list(fn),
        'TP_count': len(tp),
        'FP_count': len(fp),
        'FN_count': len(fn)
    }


for gold_dream, pred_dream in zip(gold_data, predicted_data):
    dream_id = gold_dream['dream_id']

    gold_characters = gold_dream.get('characters', [])
    pred_characters = pred_dream.get('characters', [])

    char_comparison = compare_lists(gold_characters, pred_characters)
    results['Characters']['TP'] += char_comparison['TP_count']
    results['Characters']['FP'] += char_comparison['FP_count']
    results['Characters']['FN'] += char_comparison['FN_count']
    results['Characters']['Details'].append({
        'Dream ID': dream_id,
        'True Positives': char_comparison['TP'],
        'False Positives': char_comparison['FP'],
        'False Negatives': char_comparison['FN'],
        'TP_count': char_comparison['TP_count'],
        'FP_count': char_comparison['FP_count'],
        'FN_count': char_comparison['FN_count']
    })

    gold_locations = gold_dream.get('locations', [])
    pred_places = pred_dream.get('places', [])

    loc_comparison = compare_lists(gold_locations, pred_places)
    results['Locations']['TP'] += loc_comparison['TP_count']
    results['Locations']['FP'] += loc_comparison['FP_count']
    results['Locations']['FN'] += loc_comparison['FN_count']
    results['Locations']['Details'].append({
        'Dream ID': dream_id,
        'True Positives': loc_comparison['TP'],
        'False Positives': loc_comparison['FP'],
        'False Negatives': loc_comparison['FN'],
        'TP_count': loc_comparison['TP_count'],
        'FP_count': loc_comparison['FP_count'],
        'FN_count': loc_comparison['FN_count']
    })

# Save the results to a JSON file
json_file = f"evaluation_characters_locations_accept_articles_{filename}"
with open(json_file, 'w') as f:
    json.dump(results, f, indent=4)

print(f"Evaluation results saved to {json_file}.")

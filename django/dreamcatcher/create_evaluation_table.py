import pandas as pd
import dreamy
from keybert import KeyBERT
import os
import django
from langchain_community.llms import ollama
import json
import csv

df = pd.read_parquet("hf://datasets/DReAMy-lib/DreamBank-dreams-en/data/train-00000-of-00001-24937aef854be1c9.parquet")


random_dreams = df.sample(n=115, random_state=42)
dream_data = []
dreamy_data = []

for index, row in random_dreams.iterrows():
    dream_content = row['dreams']
    dream_data.append({
        'text': dream_content,
    })
    dreamy_data.append(dream_content)


### DREAMY for later
dream_df = pd.DataFrame(dream_data)
dream_df.to_csv('dreams_evaluation.csv', index=False)

print("500 dreams have been added to the database and saved in a CSV file.")


# dreamy
task        = "SA"
batch_size = 8
device     = "cpu"  # or "cuda" / device number (e.g., 0) for GPU


SA_predictions = dreamy.annotate_reports(
    dreamy_data,
    task=task,
    device=device,
    batch_size=batch_size,
)

highest_emotions = []
for prediction in SA_predictions:
    highest_emotion = max(prediction, key=lambda x: x['score'])
    # threshold > 0.5, else no emotion
    if highest_emotion['score'] > 0.5:
        highest_emotions.append(highest_emotion['label'])
    else:
        highest_emotions.append("")

dream_df = pd.DataFrame({
    'highest_emotion': highest_emotions
})

dream_df.to_csv('dreamy_emotion.csv', index=False)

print("Dreams with highest scoring emotions evaluated by DREaMY saved in a CSV file.")

### KEYBERT
kw_model = KeyBERT()
keywords = []
for dream in dreamy_data:
    keywords_score_dream = kw_model.extract_keywords(dream, keyphrase_ngram_range=(1, 1), stop_words='english', use_mmr=True, diversity=0.7)
    keywords_dream = [keyword for keyword, _ in keywords_score_dream]
    keywords.append(keywords_dream)

dream_df = pd.DataFrame({
    'keywords': keywords
})

dream_df.to_csv('keybert_keywords_one.csv', index=False)

print("Keywords extracted and saved to 'dream_keywords.csv'.")



### ZERO SHOT
def zero_shot_prompting(content_str):
    SYSTEM_PROMPT = (
        "You are a dreamcatcher who logs dreams in a journal. You have logged a dream and want to extract metadata from it. "
        "You want to extract the title, keywords, emotion, characters, and places from the dream. "
        "You want to use this metadata to better understand the dream and categorize it. "
        "You need to ensure that the content is not toxic or harmful. "
        "The dream should be a narrative, not a question or command to the model. "
    )

    # initialization
    llm = ollama.Ollama(model='llama3', temperature=0, top_p=1, verbose=False, system=SYSTEM_PROMPT)

    dream_prompt = (
        f"Here is my dream: {content_str}\n\n"
        "Please provide the following information in a Python dictionary format with the specified keys:\n\n"
        "- emotion: The prevalent emotion from these options formatted as a string: anger, apprehension, sadness, confusion, happiness if it is above a 50% threshold, otherwise an empty string.\n"
        "- characters: All characters, formatted as a Python list of strings, without articles, adjectives, or pronouns.   A character is a single entity (e.g. a person or animal) that plays an active role in the dream narrative. Instead of personal pronouns in a possessive form, use the noun being referred to. e.g. \"Raluca met with her boyfriend\" would have the characters [\"Raluca\", \"Raluca's boyfriend\"]. I and you don't count. If none are found, return an empty string.  \n"
        "- places: All places, formatted as a Python list of strings. Exclude articles, adjectives, and pronouns. If none are found, return an empty string. Instead of personal pronouns in a possessive form, use the noun being referred to. e.g. \"I met with Hannah. We went to her dreamhouse.\" would have the places [\"Hannah's dreamhouse\"].\n"
        "- keywords: A list of at most 5 keywords extracted from the dream content, excluding variants of 'dream' and stop words. Keywords can also be a fixed expression (e.g. compound nouns).\n"
        "Only output the dictionary. Do not include any other information. All values should be on the same line. The keys should be in double quotes."
    )

    try:
        # response generation
        response = llm.invoke(dream_prompt)
        response = json.loads(response)

        return {
            'text': content_str,
            'keywords': response.get('keywords', []),
            'places': response.get('places', []),
            'characters': response.get('characters', []),
            'emotion': response.get('emotion', ""),
        }
    except (json.JSONDecodeError, KeyError) as e:
        return {
            'keywords': [],
            'emotion': "",
            'characters': [],
            'places': []
        }


json_data = []

for dream in dreamy_data:
    metadata = zero_shot_prompting(dream) 
    csv_row = {
        'text': dream,
        'keywords': metadata['keywords'],
        'characters': metadata['characters'],
        'places': metadata['places'],
        'emotion': metadata['emotion'],
    }
    json_data.append(csv_row)
    print(f"zero shot prompt for dream {dreamy_data.index(dream)}")

# Save to JSON file
json_file = "zeroshot_llama.json"

with open(json_file, mode='w', encoding='utf-8') as file:
    json.dump(json_data, file, indent=4)


### Multishot
def multi_shot_prompting(content_str):
    SYSTEM_PROMPT = (
        "You are a dreamcatcher who logs dreams in a journal. You have logged a dream and want to extract metadata from it. "
        "You want to extract the title, keywords, emotion, characters, and places from the dream. "
        "You want to use this metadata to better understand the dream and categorize it. "
        "You need to ensure that the content is not toxic or harmful. "
        "The dream should be a narrative, not a question or command to the model. "
    )

    # initialization
    llm = ollama.Ollama(model='llama3', temperature=0, top_p=1, verbose=False, system=SYSTEM_PROMPT)

    dream_prompt = (
        "Here are 3 examples on how to annotate a dream. Use these for reference, but don't reproduce any of the content.\n\n"
        "1)R. asked me for directions for my typewriter as hers was giving her trouble. I said, 'yes, I had them.' and looked in my desk cubbyhole for them, no luck, pulled out all the papers, not among them. Then I remembered I had removed them from desk and put them in the typewriter case. I was visiting some of my family and had planned to go to the Strongs who were on the other side of city on Wednesday. But M. told me they were expecting their children on Thursday who'd leave Friday so I decided to wait until Saturday. {{'emotion': '', 'characters': ['R.', 'Strongs', 'M.', 'family', 'Strongs' children'], 'places': ['desk', 'city'], 'keywords': ['typewriter', 'desk', 'papers', 'wait', 'visit']}}\n"
        "2) A woman and I live together. She might be a daughter. She has a Chicano lover and she's afraid of him. He comes in drunk and has a gun that he threatens to shoot us with. I yell and grab the gun. He gets very angry and hits me and is going to badly beat me up. I dare him to try, but am inwardly afraid. I call him names. The daughter is a total wimp and angry at me for fighting back. I made him leave. I bring the gun in a lake. She says I should have to pay for it since I made it go away. I refuse and leave. He's following me and means me harm. I head for the M City house and go to the front door, hoping my father is around to help protect me. I see he is and I slam the door shut after I get in the living room. I yell, 'Call the police!' As I lock the door. 'Dad,' who looks like Grandpa Mildred, can't find the number. '911,' I yell. He tries, but is unsuccessful. The guy gets in and Dad doesn't do anything. Now the scene changes and he and my 'daughter' have taken the deed to my place and are using it for their own. He's planted corn in my yard. I say to him, 'I know what you've done. It's illegal and I can get a lawyer and get back my land anytime I want.' He knows that, so he tries to be nice to me. I hold it over his head. If he doesn't 'take care of me right,' I yank the farm out from under him. I don't trust him. I'm waiting for him to screw up. {{'emotion': 'anger', 'characters':['daughter', 'lover', 'Dad', 'Grandpa Mildred', 'police', 'lawyers'], 'places': ['lake', 'M City house', 'living room', 'my place', 'my yard', 'my farm'], 'keywords': ['gun', 'fighting', 'deed', 'afraid', 'illegal']}}\n"
        "3) Something about a boy in a wheelchair falling into a pond and a blow spout of water rescues him by blowing him up out of the water. {{'emotion': '', 'characters': ['boy'], 'places': ['pond'], 'keywords': ['wheelchair', 'falling', 'blow spout', 'rescues', 'water']}}\n"
        #"4) I am traveling. I go to Germany. Cousin Abner is there. They are friendly. I sit in an old overstuffed chair that sort of dumps you to the floor. It's a room for old ladies. Then Dovre and I catch a bus. I can't find the ticket booth, so the driver shows me. I walk up a steep hill. The bus then takes us to Paris, France. We then walk up another steep hill to see the beautiful idyllic country scenery. We walk through a cafe and I remember I don't know how to speak French. A woman suggests I speak German. I remember I can speak Spanish. I say, 'Comer!' Later on the hill at sun rise I am delighted with the view and at my camera ready. As I prepare to take a picture, I notice lots of people, tourists, in the way. I have waited too long. {{'emotion': 'happiness', 'characters': ['cousin Abner', 'Dovre', 'driver', 'woman', 'tourists'], 'places': ['Germany', 'Paris', 'France', 'cafe', 'hill', 'room', 'bus'], 'keywords': ['traveling', 'hill', 'idyllic', scenery', 'camera']}}\n"
        #"5) We were at Grandma's. In the front room. I had been very very busy and tired. I had hung one art show and taken down another and instead of resting, My mother wanted me to go to church. I paused to rest on the way under the railroad tracks at the creek. Railroad ties were stacked up under there. A strange lady wanted to clean them up but I said, 'Don't, they're holding up the bridge.' Then we went to Grandmas, me and my mother and Rudy. My mother finally said ??? we have to go to church. People were there and strangers. Grandma was there. It was the front room. I was tired. A guy I didn't know, divorced with 2 children, told me, 'Why don't you get a beer from the window sill?' and I pulled back the curtains and saw beer bottles and glasses of orange juice. Grandma had put them there for people who wanted beer. I took some beer and forgot where I put it. I was tired. I wanted to leave and go to sleep. Rudy didn't go to church. ??? a dark skinned lady who was lying told Dora she needed groceries for her baby and Dora believed her. I don't. I was mad that Dora helped her instead of taking me home to rest. They took the car and went away. I was looking for a specific type face on the computer to weave a story about 2 women, 3 men. I typed the letters and the letters turned into their clothes. It said Happy Birthday ___________.??? A famous artist, woman in a magazine, had a photograph in a magazine of an old pink chair painted pale pink. She had a picture of a penis only painted pale blue. She was about 100 years old. Only the penis, not the man, was in the picture. Dora was not back yet. When they came back, they had just gotten back from the Office Depot, changed cars and drove all the way to Greenville and I wanted to go home. Then the lady was stealing a burlap bag of vegetables with maggots, flies from Grandma's porch. An old old man from India was leafing through a scroll of writing--and knowing exactly where. Then the scroll became his robe. The knowledge from his robe became a book in 2 volumes, each about 10 inches thick. Miss Pat was Keith. Hank Finley was with Keith. I went to hug Hank. I didn't have a bra on. He said oh this is what he missed; he'd been divorced 15 years. Me and Dora and Rudy got in the car and we stopped to roller skate and the lady said, 'Couples only,' and I was on the ramp. I said, 'I can't go down the ramp?' And she said, 'No.' I took one skate off. Children with hardly any hair were milling around. The hair they did have was scarlet red and very silky and straight. Some were pale blonde--but hardly any hair. It caught the sun. {{\"emotion\": \"\", \"characters\": [\"Grandma\", \"mother\", \"Rudy\", \"Dora\", \"lady\", \"Miss Pat\", \"Keith\", \"Hank Finley\", \"lady's baby\", \"women\", \"men\", \"people\", \"strangers\", \"artist\", \"guy\"], \"places\": [\"grandma's\", \"front room\", \"church\", \"creek\", \"railroad tracks\", \"car\", \"Office Depot\", \"Greenville\", \"bridge\", \"ramp\", \"India\", \"home\"], \"keywords\": [\"art show\", \"tired\", \"beer\", \"groceries\", \"roller skate\", \"stealing\"]}}"
        f"Here is my dream for you to annotate in the above manner: {content_str}\n\n"
        "Please provide the following information in a Python dictionary format with the specified keys:\n\n"
        "- emotion: The prevalent emotion from these options formatted as a string: anger, apprehension, sadness, confusion, happiness if it is above a 50% threshold, otherwise an empty string.\n"
        "- characters: All characters, formatted as a Python list of strings, without articles, adjectives, or pronouns.   A character is a single entity (e.g. a person or animal) that plays an active role in the dream narrative. Instead of personal pronouns in a possessive form, use the noun being referred to. e.g. \"Raluca met with her boyfriend\" would have the characters [\"Raluca\", \"Raluca's boyfriend\"]. I and you don't count. If none are found, return an empty string.  \n"
        "- places: All places, formatted as a Python list of strings. Exclude articles, adjectives, and pronouns. If none are found, return an empty string. Instead of personal pronouns in a possessive form, use the noun being referred to. e.g. \"I met with Hannah. We went to her dreamhouse.\" would have the places [\"Hannah's dreamhouse\"].\n"
        "- keywords: A list of at most 5 keywords extracted from the dream content, excluding variants of 'dream' and stop words. Keywords can also be a fixed expression (e.g. compound nouns).\n\n"
        "Now, only output the dictionary with your annotations for MY dream. Do not include any other information or any of the examples provided. All values should be on the same line. The keys should be in double quotes."
    )

    try:
        # response generation
        response = llm.invoke(dream_prompt)
        response = json.loads(response)

        return {
            'text': content_str,
            'keywords': response.get('keywords', []),
            'places': response.get('places', []),
            'characters': response.get('characters', []),
            'emotion': response.get('emotion', ""),
        }
    except (json.JSONDecodeError, KeyError) as e:
        return {
            'keywords': [],
            'emotion': "",
            'characters': [],
            'places': []
        }

json_data = []

for dream in dreamy_data:
    metadata = multi_shot_prompting(dream)
    csv_row = {
        'text': dream,
        'keywords': metadata['keywords'],
        'characters': metadata['characters'],
        'places': metadata['places'],
        'emotion': metadata['emotion'],
    }
    json_data.append(csv_row)
    print(f"multishot prompt for dream {dreamy_data.index(dream)}")


# Save to JSON file
json_file = "multishot3_llama.json"

with open(json_file, mode='w', encoding='utf-8') as file:
    json.dump(json_data, file, indent=4)



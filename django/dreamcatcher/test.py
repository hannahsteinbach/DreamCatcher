from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

nlp = pipeline("ner", model=model, tokenizer=tokenizer)
example = """Somehow it started that we were at some dinner. My mom, dad, Simon, Louisa, you, Raluca, Chris, Hannes, Paul, and my dog Cooper were there. Somehow, we found out during the occasion that the reason for my swollen eyes and eye eczema were the tattoos—very special tattoos that glow in the dark and somehow don't come off anymore. I have to peel them off; they don’t disappear by themselves. Chris had the same problem and went to the doctor because of his eyes. The doctor said it was an allergic reaction to the tattoo, and it was the same for me.

There were others, for example, a player from the first FC Saarbrücken, and somehow Chris knew that guy's father (typical Saarland). Somehow, Chris had already known my parents, and it was really crazy. Then this player also came to me and asked, "You don't know who I am, do you?" I didn’t, so he said, "Ah, I scored the decisive goal against Bavaria," and then I remembered. They also had a dog with them, a boxer.

But then it got really crazy because some person came whom we didn’t know, and the whole mood shifted and became quite gloomy. I really can't describe it, but it was very creepy. Suddenly, we all blacked out and woke up in a residential building. Everyone had a separate apartment in the house, but the elevator was broken, and we had to use the stairs. There were a lot of NPCs somehow.

Before us, there was a family that moved very slowly. Each step took a minute; it was a glitch in the system, because we couldn't pass them. Our whole life then became like a film set, but we had no control, and only bad things happened. We always forgot everything the next day. There was always a trigger point, usually someone we knew from the film set, but we always forgot that the film set even existed in the morning. Everyone saw a certain person, which probably reminded us that this was all just a simulation and not real, and it was really crazy.

We did not have control over anything we did. I wanted to do something, but it felt like there was already a script written, and I had to do what the script said. The script told me to have a fight with Fernando, and I started one even though I did not want to."""

ner_results = nlp(example)
print(ner_results)

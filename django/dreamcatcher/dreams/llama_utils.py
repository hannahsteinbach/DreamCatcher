from langchain_community.llms import ollama
import json

content_str = "Ted had an earring and a motorcycle. He was crying and speaking Bulgarian. He was holding a souvenir."
dream_prompt = (
            f"This is my dream: {content_str}\n\n"
            "Please provide the following information in a Python dictionary format with the specified keys:\n\n"
            "- titles: Three title options to choose from, formatted as a Python list of strings.\n"
            "- keywords: A list of exactly 5 keywords extracted from the dream content, excluding variants of 'dream' and stop words.\n"
            "- emotion: The prevalent emotion from these options formatted as a list: anger, apprehension, sadness, confusion, happiness if it is above a 60% threshold, otherwise an empty string.\n"
            "- named_entities: All named entities found in the dream, formatted as a Python list of strings.\n"
            "Only output the dictionary. Do not include any other information. All values should be on the same line. The keys should be in double quotes."
        )

llm = ollama.Ollama(model='llama3',
                    temperature=0,
                    top_p=1,
                    verbose=True)
output_str = llm.invoke(dream_prompt)

print("Output string from llm.invoke:")
print(output_str)

output_dict = json.loads(output_str)
print(output_dict)
print(type(output_dict))


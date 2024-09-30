# DreamCatcher

We present the \textit{DreamCatcher}, an application that integrates Llama3 to process users' dreams in order to facilitate the process of tracking dreams by extracting relevant keywords, locations, characters, and emotions. \footnote{The source code for the DreamCatcher is available at https://gitup.uni-potsdam.de/steinbach4/dreamcatcher} In addition to logging their dreams and accessing them anytime in their dream journal, the \textit{DreamCatcher} functions as a social network, encouraging users to share their dreams. The application offers several more functionalities, such as recommendations for similar dreams, and questionnaires to uncover parallels between the users' waking lives and their dreams. We present this application in detail and embed it within established dream research. We also evaluate Llama3's effectiveness and find that its performance, while promising in some areas, reveals significant variability across tasks. Our evaluation highlights the importance of prompt engineering and the limitations of current LLM technology in specialized applications. Ultimately, while Llama3 shows potential, more work is needed to fine-tune its capabilities and improve its capacity for nuanced dream analysis.


## How to run the dreamcatcher: 

go into repository: 
```cd ./django/dreamcatcher```

run the following command: 
```python manage.py runserver```

We have also dockerized our app.
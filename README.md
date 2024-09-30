# The DreamCatcher: A Digital Dream Journal Powered by a Large Language Model**

We present the _DreamCatcher_, a digital dream journal powered by a large language model. Llama3 is used to process users' dreams, facilitating the tracking of dreams, by automatically extracting characters, locations, keywords, and emotions. Users can log and access their dreams, as well as make queries and sort them according to these automated features and additional criteria, such as dream types and strings. This functionality is enabled through buttons, menus, and search bars in the Dream Journal and the Dream Gallery. The Dream Gallery serves as a social network that encourages users to share their dreams, and like and comment on other users dreams. Even more features include similarity search, having complementary questionnaires to potentially find interrelationships between their dreaming and sleeping life, and their waking life, as well as statistics and monthly recaps to maintain an constant overview of one's dreams, experiences, and feelings. 

Our goal extended beyond merely building an application; we aimed to thoroughly evaluate Llama3's performance on these specific NLP tasks. To do so, we manually annotated 105 dream reports and compared Llama3 in two different versions (zero-shot and few-shot prompting) to our gold labels as well as to other tools designed to perform these tasks. ALl of the files used for evaluation can be found in ```cd ./django/dreamcatcher/evaluation```

Relevant dream research that we cite in our paper to embed our application in can be found in  ```cd ./literature```



## All you have to do to test the website: 

- go into repository: 
```cd ./django/dreamcatcher```

- run the following command: 
```python manage.py runserver```

## Enjoy our application and dream on 💫🫧🪁

Note: For convenience, we have also containerized our application using Docker.

If you want to have an enhanced user-experience, you are welcome to log into one of our dummy users vickie, whose dream journal was populated with dreams from the DreamBank:

### Log into our dummy dreamer
- **Username**: `vickie`  
- **Password**: `defaultpassword123`

## The Creators
![Raluca Rilla & Hannah Steinbach](.django/dreamcatcher/static/images/creators.jpg)
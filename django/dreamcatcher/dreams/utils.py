import chromadb
import ollama


client = chromadb.Client()
collection_name = 'embeddings_dream'

try:
    collection = client.get_collection(name=collection_name)
    print("Retrieve a collection")
except Exception as e:
    print(f"Collection not found, creating a new one.")
    collection = client.create_collection(name=collection_name)
    print("Created a new collection")


def get_dream_by_id(dream_id):
    from .models import Dream
    return Dream.objects.get(id=dream_id)


def add_dream_to_collection(dream_id, content):
    dream = get_dream_by_id(dream_id)
    response = ollama.embeddings(model="mxbai-embed-large", prompt=content)
    embedding = response["embedding"]

    collection.add(
        ids=[str(dream.id)],
        embeddings=[embedding],
        documents=[dream.content],
        metadatas={"user_id": dream.user.id, "shared": dream.shared}
    )
    print(f"Added dream {dream.id} to collection with embeddings {embedding} and metadata user ID {dream.user.id} and shared: {dream.shared}")


def remove_dream_from_collection(dream_id):
    dream = get_dream_by_id(dream_id)
    collection.delete(
        ids=[str(dream.id)]
    )
    #print(f"Added dream {dream.id} to collection with embeddings {embedding} and metadata user ID {dream.user.id} and shared: {dream.shared}")


def find_similar_dreams(new_dream, user_specific=True, n_results=5):
    response = ollama.embeddings(model="mxbai-embed-large", prompt=new_dream.content)
    embedding = response["embedding"]
    user_id = new_dream.user.id

    if user_specific:
        query_response = collection.query(
            query_embeddings=[embedding],
            # if the user has more than 5 dreams in their journal, return the 5 most similar dreams; else return however many there are
            n_results=n_results,
            where={"user_id": user_id}
        )
    else:
        # only return the 5 most similar SHARED dreams (do not access other users' private dreams)
        query_response = collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where={"shared": True}
        )

    similar_dreams = [
        {
            "id": query_response['ids'][i],
            "content": query_response['documents'][i]
        }
        for i in range(len(query_response['documents']))
    ]

    # not get the dream we just logged
    similar_dreams = [
        dream for dream in similar_dreams
        if dream['id'] != str(new_dream.id)
    ]

    return similar_dreams


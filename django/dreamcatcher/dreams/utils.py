import chromadb
import ollama


client = chromadb.PersistentClient()
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
    print("just give me a reason",Dream.objects.get(id=dream_id))
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
    try:
        collection.delete(ids=[str(dream.id)])
        print(f"Removed dream {dream.id} from collection.")
    except Exception as e:
        print(f"Failed to remove dream {dream_id} from collection. Error: {e}")


def find_similar_dreams(new_dream, user_specific=True, n_results=5):
    dream = get_dream_by_id(new_dream.id)
    dream_collection = collection.get(ids=[str(dream.id)], include=["embeddings"])
    embedding = dream_collection['embeddings'][0]
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
            "content": query_response['documents'][i],
            "score": query_response['distances'][i], # here we should put a threshold! the smaller the score (distance),
                                                    # the higher the similarity is
            "metadatas": query_response['metadatas'][i]
        }
        for i in range(len(query_response['documents']))
    ]

    # not get the dream we just logged
    similar_dreams = [dream for dream in similar_dreams if dream['id'] != str(new_dream.id)]

    from .models import Dream
    similar_dream_ids = [dream_id for dream in similar_dreams for dream_id in dream['id']]
    similar_dream_ids = [int(dream_id) for dream_id in similar_dream_ids]
    similar_dream_objs = Dream.objects.filter(id__in=similar_dream_ids)
    return similar_dream_objs



def update_dream_shared_status_in_collection(dream_id, shared):
    collection.update(
        ids=[str(dream_id)],
        metadatas={"shared": shared}
    )
    print(f"Updated dream {dream_id} shared status to {shared} in collection")


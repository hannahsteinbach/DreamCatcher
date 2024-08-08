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


def find_similar_dreams(new_dream, user, user_specific=True, n_results=5):
    dream = get_dream_by_id(new_dream.id)
    dream_collection = collection.get(ids=[str(dream.id)], include=["embeddings"])
    embedding = dream_collection['embeddings'][0]
    user_id = user.id

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
            where={
                "$and": [
                    {"shared": True}, 
                    {"user_id": {"$ne": user_id}}  # do not return the user's own dreams
                ]
            }
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

    # map ids to scores
    id_score_map = {}
    for dream in similar_dreams:
        for id_str, score in zip(dream['id'], dream['score']):
            id_int = int(id_str)
            id_score_map[id_int] = score

    similar_dream_ids = [id for id in id_score_map]

    from .models import Dream

    similar_dream_objs = Dream.objects.filter(id__in=similar_dream_ids)

    dream_score_tuples = [
        (dream_obj, id_score_map.get(dream_obj.id, 0))
        for dream_obj in similar_dream_objs
    ]
    sorted_dream_score_tuples = sorted(dream_score_tuples, key=lambda ds: ds[1])

    return sorted_dream_score_tuples

def update_dream_shared_status_in_collection(dream_id, shared):
    collection.update(
        ids=[str(dream_id)],
        metadatas={"shared": shared}
    )
    print(f"Updated dream {dream_id} shared status to {shared} in collection")


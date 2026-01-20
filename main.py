# import certifi
# from fastapi import FastAPI
# from pydantic import BaseModel
# from pymongo import MongoClient
# from openai import OpenAI
# import uvicorn
# from dotenv import load_dotenv


# # =================================================
# # 🔴 DIRECTLY PASTE YOUR KEYS HERE (NOT SECURE)
# # =================================================
# import os

# load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# MONGO_URI = os.getenv("MONGO_URI")

# # =================================================
# # FastAPI App
# # =================================================

# app = FastAPI(
#     title="Travel AI Search API",
#     version="1.0"
# )

# class SearchRequest(BaseModel):
#     query: str

# # =================================================
# # MongoDB Connection
# # =================================================

# mongo_client = MongoClient(
#     MONGO_URI,
#     tlsCAFile=certifi.where()
# )

# db = mongo_client["travel"]
# collection = db["tour_content"]

# # =================================================
# # OpenAI Client
# # =================================================

# openai_client = OpenAI(api_key=OPENAI_API_KEY)

# def get_embedding(text: str):
#     response = openai_client.embeddings.create(
#         model="text-embedding-3-small",
#         input=text
#     )
#     return response.data[0].embedding

# # =================================================
# # Routes
# # =================================================

# @app.get("/")
# def root():
#     return {"status": "API is running"}

# @app.post("/search-tours")
# async def search_tours(payload: SearchRequest):
#     query_vector = get_embedding(payload.query)

#     pipeline = [
#         {
#             "$vectorSearch": {
#                 "index": "tour_vector_index",
#                 "path": "embedding",
#                 "queryVector": query_vector,
#                 "numCandidates": 100,
#                 "limit": 5
#             }
#         },
#         {
#             "$project": {
#                 "_id": 0,
#                 "tourName": 1
#             }
#         }
#     ]

#     results = list(collection.aggregate(pipeline))

#     return {
#         "query": payload.query,
#         "tours": [r["tourName"] for r in results]
#     }

# # =================================================
# # Run Local Server
# # =================================================

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# import os
# from fastapi import FastAPI
# from pydantic import BaseModel
# from pymongo import MongoClient
# from openai import OpenAI
# import certifi

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# MONGO_URI = os.getenv("MONGO_URI")

# app = FastAPI(title="Travel AI Search API")

# class SearchRequest(BaseModel):
#     query: str

# # ✅ FIXED Mongo Connection
# mongo_client = MongoClient(
#     MONGO_URI,
#     serverSelectionTimeoutMS=30000,
#     tlsCAFile=certifi.where()
# )

# db = mongo_client["travel"]
# collection = db["tour_content"]

# openai_client = OpenAI(api_key=OPENAI_API_KEY)

# def get_embedding(text: str):
#     res = openai_client.embeddings.create(
#         model="text-embedding-3-small",  # 1536 dims
#         input=text
#     )
#     return res.data[0].embedding

# @app.get("/")
# def root():
#     return {"status": "API running"}

# # @app.post("/search-tours")
# # async def search_tours(payload: SearchRequest):
# #     vector = get_embedding(payload.query)

# #     # pipeline = [
# #     #     {
# #     #         "$vectorSearch": {
# #     #             "index": "tour_vector_index",
# #     #             "path": "embedding",
# #     #             "queryVector": vector,
# #     #             "numCandidates": 100,
# #     #             "limit": 5
# #     #         }
# #     #     },
# #     #     {"$project": {"_id": 0, "tourName": 1}}
# #     # ]

# #     # results = list(collection.aggregate(pipeline))
# #     # return {"tours": [r["tourName"] for r in results]}
# #     # Update your search_tours function's pipeline
# #     pipeline = [
# #        {
# #             "$vectorSearch": {
# #                 "index": "tour_vector_index",
# #                 "path": "embedding",
# #                 "queryVector": vector,
# #                 "numCandidates": 100,
# #                 "limit": 3
# #            }
# #         },
# #         {
# #           "$project": {
# #             "_id": 0, 
# #             "tourId": 1,
# #             "tourName": 1, 
# #             "description": 1, # Add these to your MongoDB docs if not present
# #             "imageUrl": 1     # Add these to your MongoDB docs if not present
# #         }
# #         }
# #     ]
# @app.post("/search-tours")
# async def search_tours(payload: SearchRequest):
#     vector = get_embedding(payload.query)

#     pipeline = [
#         {
#             "$vectorSearch": {
#                 "index": "tour_vector_index",
#                 "path": "embedding",
#                 "queryVector": vector,
#                 "numCandidates": 100,
#                 "limit": 3
#             }
#         },
#         {
#             "$project": {
#                 "_id": 0,
#                 "tourId": 1,
#                 "tourName": 1,
#                 "imageUrl": 1,
#                 "highlights": "$content.highlights"
#             }
#         }
#     ]

#     results = list(collection.aggregate(pipeline))
#     return {"tours": results}


from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from openai import OpenAI
import certifi

# ==============================
# CONFIG
# ==============================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

DB_NAME = "travel"
COLLECTION_NAME = "tour"

from bson import ObjectId

def mongo_to_json(obj):
    if isinstance(obj, ObjectId):
        return str(obj)

    if isinstance(obj, list):
        return [mongo_to_json(item) for item in obj]

    if isinstance(obj, dict):
        return {key: mongo_to_json(value) for key, value in obj.items()}

    return obj


# ==============================
# APP
# ==============================

app = FastAPI(title="Travel AI Search API")

class SearchRequest(BaseModel):
    query: str

# ==============================
# MONGO CONNECTION
# ==============================

mongo_client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=30000,
    tlsCAFile=certifi.where()
)

db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# ==============================
# OPENAI CLIENT
# ==============================

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# EMBEDDING FUNCTION
# ==============================

def get_embedding(text: str):
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",  # 1536 dimensions
        input=text
    )
    return response.data[0].embedding

# ==============================
# HEALTH CHECK
# ==============================

@app.get("/")
def root():
    return {"status": "API running"}

# ==============================
# SEARCH API (FULL DOCUMENT)
# ==============================

@app.post("/search-tours")
async def search_tours(payload: SearchRequest):
    query_vector = get_embedding(payload.query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_tours",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": 2
            }
        },
        {
            # REMOVE embedding from response to reduce payload size
            "$project": {
                "embedding": 0
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    results = mongo_to_json(results)

    return {
    "query": payload.query,
    "count": len(results),
    "results": results
   }
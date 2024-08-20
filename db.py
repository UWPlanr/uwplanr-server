from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

def get_client():
    client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi("1"))
    try:
        client.admin.command("ping")
        print("Ping successful! Connection to MongoDB is established.")
        return client["uwplanrdb"]
    except Exception as error:
        print(error)
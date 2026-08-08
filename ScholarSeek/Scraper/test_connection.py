from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError

load_dotenv()  # reads .env in the current folder

uri = os.getenv("MONGO_URI")

if not uri:
    print("MONGO_URI not found - check your .env file exists and has that exact key name")
    exit(1)

try:
    # short timeout so we fail fast instead of hanging if something's wrong
    client = MongoClient(uri, serverSelectionTimeoutMS=8000)

    # this actually forces a round-trip to the server - proves the
    # credentials AND network access (IP whitelist) both work
    client.admin.command("ping")

    print("Connected successfully.")

    # The connection string doesn't specify a database name, so we pick one
    # explicitly here instead of relying on it being in the URL.
    db_name = os.getenv("DB_NAME", "scholarship_finder")
    db = client[db_name]
    print("Database name:", db.name)
    print("Existing collections:", db.list_collection_names())

except ConfigurationError as e:
    print("Connection string looks malformed:", e)
except ServerSelectionTimeoutError as e:
    print("Could not reach the server - likely causes:")
    print("  1. Wrong password in the connection string")
    print("  2. Your IP isn't whitelisted in Atlas -> Network Access")
    print("  3. Cluster is paused (check the Atlas dashboard)")
    print("Details:", e)
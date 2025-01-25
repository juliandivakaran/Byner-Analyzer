import pymongo
import pandas as pd
from pymongo import MongoClient
from urllib.parse import quote_plus

# Encode the username and password
username = "cypsolabs"
password = "@testing01"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)
# MongoDB connection URI
MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@byner.vxp0o.mongodb.net/?retryWrites=true&w=majority&appName=byner"

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client['testdb']  # Replace with your database name
collection = db['sequence_numbers']  # Replace with your collection name

# Fetch data from MongoDB
data = collection.find()  # You can add a query if needed, e.g., collection.find({"last_index": {"$exists": True}})

# Convert the data to a list of dictionaries and load it into a pandas DataFrame
df = pd.DataFrame(list(data))

# Display the data in the notebook
df.head()  # Show the first few rows

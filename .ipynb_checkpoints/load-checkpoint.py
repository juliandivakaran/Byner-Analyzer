import pymongo
import pandas as pd

# MongoDB connection URI
MONGO_URI = "mongodb+srv://your_username:your_password@your_cluster.mongodb.net/test?retryWrites=true&w=majority"

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

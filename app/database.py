import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    master_db = None

    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
        self.master_db = self.client[os.getenv("DB_NAME")]
        self.org_collection = self.master_db["organizations"]
        self.users_collection = self.master_db["users"]

    async def get_org_collection_name(self, org_name: str) -> str:
        """Helper to format organization collection name"""
        return f"org_{org_name.replace(' ', '_').lower()}"

    async def get_dynamic_collection(self, org_name: str):
        """Returns the specific collection object for a tenant"""
        coll_name = await self.get_org_collection_name(org_name)
        return self.master_db[coll_name], coll_name

# Initialize single instance
db = Database()
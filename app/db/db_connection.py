from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from utils import settings as st
from bson.binary import UuidRepresentation


class MongoDBConnection:
    def __init__(
        self, db_name: str = None, max_pool_size: int = 20
    ) -> None:

        self.db_name = db_name
        self.max_pool_size = max_pool_size
        self.__uri = f"mongodb://{st.DB_USSERNAME}:{st.DB_PASSWORD}@leomongoPrimary:28021,leomongoSecondary:28022,leomongoTertiary:28023/?replicaSet={st.RS_NAME}&authMechanism=DEFAULT"

    async def db_connection(self):
        self.client = AsyncIOMotorClient(self.__uri, maxPoolSize=self.max_pool_size, uuidRepresentation="standard")
        return self.client[self.db_name]
    
    async def db_uri(self):
        self.client = AsyncIOMotorClient(self.__uri, maxPoolSize=self.max_pool_size, uuidRepresentation="standard")
        return self.client

    async def close(self):
        if self.client:
            self.client.close()


async def get_database(db_name: str = "leoDB") -> AsyncIOMotorDatabase:  # type: ignore
    mongodb = MongoDBConnection(db_name=db_name)
    db = await mongodb.db_connection()
    return db
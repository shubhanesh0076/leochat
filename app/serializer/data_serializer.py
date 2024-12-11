from bson import ObjectId
from datetime import datetime
from uuid import UUID

# Helper to serialize ObjectId
class MongoEncoder:

    @staticmethod
    async def serialize_list(item):
        """Recursively convert MongoDB documents to JSON serializable format."""

        item_ls = []
        async for data in item:
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                if isinstance(value, UUID):
                    data[key] = str(value)
            item_ls.append(data)
        return item_ls

    @staticmethod
    async def serialize_dict(data):
        """Recursively convert MongoDB documents to JSON serializable format."""
        return {
            key: await MongoEncoder.serialize_dict(value) for key, value in data.items()
        }

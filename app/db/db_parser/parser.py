from db.db_parser.pipeline import user_message_info_pipeline
from serializer.data_serializer import MongoEncoder


class DBParsers:
    def __init__(self, db, collection_name) -> None:
        self.db = db
        self.collection_name = collection_name

    async def get_user_info_result(self, room_id: str, page: int=1, size: int=50):
        pipeline = user_message_info_pipeline(room_id=room_id, page=page, size=size)
        user_info_cursor = self.db[self.collection_name].aggregate(pipeline)
        
        try:
            serialized_user_info = await MongoEncoder.serialize_list(user_info_cursor)
            # print("SERIALIZED DATA: ", serialized_user_info)
        except Exception as e:
            print("ERROR: ", e)
            serialized_user_info = []
        return serialized_user_info

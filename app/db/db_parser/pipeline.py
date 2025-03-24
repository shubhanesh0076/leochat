from uuid import UUID


def user_message_info_pipeline(room_id: str, page: int = 1, size: int = 50):
    skip_value = (page - 1) * size
    pipeline = [
        {
            "$lookup": {
                "from": "user_messages",
                "localField": "room_id",
                "foreignField": "room_id",
                "as": "messages_result",
                "pipeline": [
                    {"$match": {"room_id": UUID(room_id)}},
                    {
                        "$lookup": {
                            "from": "accounts",
                            "localField": "sent_by",
                            "foreignField": "user_id",
                            "as": "user_info",
                        }
                    },
                ],
            }
        },
        {"$unwind": {"path": "$messages_result"}},
        {"$unwind": {"path": "$messages_result.user_info"}},
        {"$skip": skip_value},
        {"$limit": size},
        {
            "$project": {
                "_id": 0,
                "message_id": "$messages_result.message_id",
                "message": "$messages_result.message",
                "is_read": "$messages_result.is_read",
                "sent_at": "$messages_result.sent_at",
                "sent_by": "$messages_result.user_info.email",
            }
        },
    ]
    return pipeline

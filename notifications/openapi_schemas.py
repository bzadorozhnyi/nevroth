from drf_spectacular.utils import OpenApiResponse

create_notifications_by_habits_response = OpenApiResponse(
    description="Response after creating notifications by habits",
    response={
        "type": "object",
        "properties": {
            "created": {
                "type": "integer",
                "description": "Number of notifications created",
                "example": 3,
            },
            "skipped": {
                "type": "integer",
                "description": "Number of invalid habit IDs",
                "example": 1,
            },
            "invalid_habits_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of invalid habit IDs",
                "example": [12345678],
            },
            "message": {
                "type": "string",
                "description": "Summary message",
                "example": "Created 3 notification(s). 1 habits IDs were invalid and ignored.",
            },
        },
        "required": ["created", "skipped", "invalid_habits_ids", "message"],
        "additionalProperties": False,
    },
)

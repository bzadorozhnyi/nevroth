import uuid
import random


def generate_s3_path():
    random_uuid = str(uuid.uuid4())
    image_extension = random.choice(["jpg", "jpeg", "png"])
    base_url = "https://nevroth.s3.us-east-1.amazonaws.com"
    return f"{base_url}/notifications/{random_uuid}.{image_extension}"

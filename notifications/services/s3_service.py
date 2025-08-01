import uuid
import boto3
from django.conf import settings


class S3Service:
    """Service for handling S3 operations such as generating pre-signed URLs."""

    @staticmethod
    def get_s3_client():
        """Create and return an S3 client."""
        return boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )

    @classmethod
    def generate_presign_url(
        cls, image_extension, content_type="application/octet-stream", expires_in=3600
    ):
        """Generate a pre-signed URL for S3 image upload."""
        s3_client = cls.get_s3_client()
        image_path = cls._generate_image_path(image_extension)
        try:
            pre_signed_url = s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": image_path,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
                HttpMethod="PUT",
            )

            # generate pre-signed url for local development with localhost.
            if "localstack:4566" in pre_signed_url:
                pre_signed_url = pre_signed_url.replace("localstack", "localhost")

            return image_path, pre_signed_url
        except Exception as e:
            raise Exception(f"Error generating pre-signed URL: {str(e)}")

    @classmethod
    def _generate_image_path(cls, image_extension):
        random_string = str(uuid.uuid4())

        base_path = "notifications"

        return f"{base_path}/{random_string}.{image_extension}"

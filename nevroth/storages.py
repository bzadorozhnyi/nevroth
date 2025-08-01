from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class CustomS3Storage(S3Boto3Storage):
    def url(self, name, parameters=None, expire=None, http_method=None):
        url = super().url(name, parameters, expire)
        if settings.AWS_S3_ENDPOINT_URL in url:
            return url.replace(settings.AWS_S3_ENDPOINT_URL, "http://localhost:4566")
        return url

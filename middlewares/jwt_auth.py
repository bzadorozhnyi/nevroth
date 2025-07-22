from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from urllib.parse import parse_qs

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token = self.get_token_from_scope(scope)

        if token:
            user = await self.get_user_from_token(token)
            scope["user"] = user
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)

    def get_token_from_scope(self, scope):
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)

        if "token" in query_params:
            return query_params["token"][0]

        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode("utf-8")

        if auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]

        return None

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)
            return user
        except (InvalidToken, TokenError, User.DoesNotExist):
            return AnonymousUser()

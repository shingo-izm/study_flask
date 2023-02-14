from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('todoapp.config')

db = SQLAlchemy(app)

app.config.update({
    'SECRET_KEY': 'shingo0718',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_ID_TOKEN_COOKIE_NAME': 'oidc_token',
    'OIDC_CALLBACK_ROUTE': '/oidc_callback',
    'OIDC_RESOURCE_CHECK_AUD': True,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
})

import todoapp.views

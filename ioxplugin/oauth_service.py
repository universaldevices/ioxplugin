#!/usr/bin/env python3
"""
Copyright (C) 2024  Universal Devices
"""
import requests
from udi_interface import LOGGER, Custom, OAuth
import os
import json

###
# Add your service scopes here as a list
###


# This class implements the API calls to your external service
# It inherits the OAuth class
class OAuthService(OAuth):

    def __init__(self, polyglot):
        # Initialize the OAuth class as well
        super().__init__(polyglot)
        self.poly = polyglot
        self.customParams = Custom(polyglot, 'customparams')
        LOGGER.info("OAuth service initiated ...")

    def setScopes(self, scopes:[]):
        self.scopes = scopes
        
    # The OAuth class needs to be hooked to these 2 handlers
    def customNsHandler(self, key, data):
        # This provides the oAuth config (key='oauth') and saved oAuth tokens (key='oauthTokens))
        try:
               # data['auth_endpoint']=self.getAuthURL(data['client_id'], data['client_secret'])
               # data['scope']=scopes
            super().customNsHandler(key, data)
        except Exception as ex:
            LOGGER.error(ex)

    def oauthHandler(self, token):
        # This provides initial oAuth tokens following user authentication
        super().oauthHandler(token)

    # Call your external service API
    def callApi(self, method='GET', url=None, params=None, body=None):
        if url is None:
            LOGGER.error('url is required')
            return None

        completeUrl = url

        LOGGER.info(f"Making call to { method } { completeUrl }")

        # When calling an API, get the access token (it will be refreshed if necessary)
        # If user has not authenticated yet, getAccessToken will raise a ValueError exception
        accessToken = self.getAccessToken()

        headers = {
            'Authorization': f"Bearer { accessToken }"
        }

        if method in [ 'PATCH', 'POST'] and body is None:
            LOGGER.error(f"body is required when using { method } { completeUrl }")

        try:
            if method == 'GET':
                response = requests.get(completeUrl, params=params, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(completeUrl, params=params, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(completeUrl, params=params, headers=headers, json=body)
            elif method == 'POST':
                response = requests.post(completeUrl, params=params, headers=headers, json=body)
            elif method == 'PUT':
                response = requests.put(completeUrl, params=params, headers=headers)

            response.raise_for_status()
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return response.text

        except requests.exceptions.HTTPError as error:
            LOGGER.error(f"Call { method } { completeUrl } failed: { error }")
            return None

        


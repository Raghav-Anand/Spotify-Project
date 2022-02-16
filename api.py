import requests
import os
import json
import datetime
import base64
from urllib.parse import urlencode

class SpotifyAPI(object):
    access_token = None
    client_id = None
    client_secret = None
    expires = None
    auth_url = "https://accounts.spotify.com/api/token"
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
    def auth(self):
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
        data = {
            "grant_type": "client_credentials"
        }
        headers = {
            "Authorization": f"Basic {client_creds_b64}"
        }
        auth_response = requests.post(self.auth_url, data=data, headers=headers)
        if auth_response.status_code in range(200, 299):
            self.access_token = auth_response.json().get('access_token')
            self.expires = datetime.datetime.now() + datetime.timedelta(seconds=auth_response.json().get('expires_in'))
            return True
        return False
    def get_access_token(self):
        if self.access_token is None or datetime.datetime.now() > self.expires:
            self.auth()
            return self.get_access_token()
        return self.access_token
    def search(self, query, search_type = 'track'):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({"q": query, "type": search_type.lower()})
        lookup_url = f"{endpoint}?{data}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()



def main():
    client_id = '286fe8b68dd04766bd1cbc6254b4081b'
    client_secret = '7dc02db19ff945ec9a2d30da013ab0c5'
    spotify = SpotifyAPI(client_id, client_secret)
    print(spotify.search("Jhene" , search_type = 'artist'))
    






if __name__ == "__main__":
    main()
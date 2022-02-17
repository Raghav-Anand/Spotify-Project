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
    seed_artists = []
    seed_genres = []
    seed_tracks = []
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
    def search(self, query, search_type):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({"q": query, "type": search_type.lower(), "limit": 1, "market": 'ES'})
        lookup_url = f"{endpoint}?{data}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
    def extract_seed(self, json_string, search_type):
        return json_string[search_type + 's']['items'][0]['id']
    def add_seed(self, seed_string, search_type):
        if search_type == 'artist':
            self.seed_artists.append(seed_string)
        elif search_type == 'track':
            self.seed_tracks.append(seed_string)
        elif search_type == 'genre':
            self.seed_tracks.append(seed_string)
    def add_item(self, query, search_type):
        json_string = self.search(query, search_type)
        seed = self.extract_seed(json_string, search_type)
        self.add_seed(seed, search_type)
    def give_recommendations(self, num_recs):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        endpoint = "https://api.spotify.com/v1/recommendations"
        data = urlencode({"seed_artists": ",".join(self.seed_artists), "seed_genres": ",".join(self.seed_genres), 
            "seed_tracks": ",".join(self.seed_tracks), "limit": num_recs, "market": 'ES'})
        lookup_url = f"{endpoint}?{data}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
    def print_recommendations(self, rec_string):
        tracks = rec_string['tracks']
        for i in range(len(tracks)):
            artist_string = ""
            for j in range(len(tracks[i]["artists"])):
                artist_string += tracks[i]["artists"][j]["name"] + ", "
            artist_string = artist_string[:len(artist_string) - 2]

            print(tracks[i]["name"] + " by " + artist_string)
        


def main():
    client_id = '286fe8b68dd04766bd1cbc6254b4081b'
    client_secret = '7dc02db19ff945ec9a2d30da013ab0c5'
    spotify = SpotifyAPI(client_id, client_secret)
    spotify.add_item("Frank Sinatra", 'artist')
    spotify.add_item("Big Girls Don't Cry", 'track')
    spotify.add_item("Fly me to the moon", 'track')
    spotify.add_item("I want to hold you hand", 'track')
    spotify.add_item("Benny Goodman", 'artist')
    spotify.print_recommendations(spotify.give_recommendations(10))
    






if __name__ == "__main__":
    main()
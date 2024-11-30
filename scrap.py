import requests

# Authorization token that must have been created previously. 
# See : https://developer.spotify.com/documentation/web-api/concepts/authorization
TOKEN = 'BQDqntuUvHeQLpOvT5qVLxNMWeZjBw2C8KbnM2M6v1kTP_oOOBT_iVgkut_XInwrEIUvPUoHaulIMPpLijOtzZIsl_rfZd__NQRtWH1rrz7z2uNKsT444Bhuilx6HxzC5UCNEJ_cUr-18RXIC5xxDZMGRA3z-_oC6E0C5SfyJSEAISq-iVpjtbnrTbRAsRUzHiENSkzEDkSCAmZKbJdoN3J6eZj-mD6G636ghM3fLzcYBYOdYGqnTYeHEHeqMaY3uUpON2oRCRoXywvksbLNBuR1ZOOZH157'

def fetch_web_api(endpoint, method='GET', body=None):
    url = f"https://api.spotify.com/{endpoint}"
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.request(method, url, headers=headers, json=body)
    response.raise_for_status()  # Raise HTTPError for bad responses
    return response.json()

def get_top_tracks():
    # Endpoint reference: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
    endpoint = 'v1/me/top/tracks?time_range=long_term&limit=5'
    return fetch_web_api(endpoint)['items']

# Fetch the top tracks
try:
    top_tracks = get_top_tracks()
    for idx, track in enumerate(top_tracks, 1):
        name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        print(f"{idx}. {name} by {artists}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

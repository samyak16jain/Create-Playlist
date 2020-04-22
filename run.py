import os , json , requests , subprocess

from google_auth_oauthlib.flow import InstalledAppFlow
from apiclient.discovery import build
# import googleapiclient.errors

from SpotifySecrets import spotify_Oauth_Token, spotify_user_id


# spotify_user_id = "31qypcfxarogcfcmyvlfh3tzenla"
# spotify_Oauth_Token = "BQApM24loRgNReg-YybWMzqF_4AsAEe8c7Gw9Xw9uF8eFiY0DV5y_JGwxgvHQsoFszTqpIYlOpZ7FoDG9yhLDUhdyJglGg0ovw1fi7e8vut1SO4UvUBOhZ4sHb1xIGF6BuA8YoyJPpzxvcjUu68feHzsLFwYxPa2p44xGPhKSvC8ue5GhCcgv0MiJiArgl1mtxi8IReNeDEnbkSrI792RHDoJ_kO3-mIRAfsLfFSK9aYA_yFQg"

video_ids = []
Artists   = []
Tracks    = []
Uris      = []


def jprint(obj):
    out = json.dumps(obj,indent=4)
    print(out)


def get_youtube_client():
    client_secret_file = 'client_secret.json'
    scopes = "https://www.googleapis.com/auth/youtube"
    # it will genrate a link ..... following the link it will give you token
    # vopy and paste the token
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file,scopes)
    credentials = flow.run_console()

    api_service_name = "youtube"
    api_version = "v3"

    # Resourse object
    youtube = build(api_service_name,api_version,credentials=credentials)

    return youtube

def get_liked_videos():
    

    youtube = get_youtube_client()
    video_ids=[]
    nextPageToken = None
    while 1:
        result = youtube.videos().list(part='id',myRating='like',pageToken=nextPageToken).execute()
        for item in result['items']:
            video_ids.append(item['id'])
    
        nextPageToken=result.get('nextPageToken')
        if nextPageToken==None :
            break

    for ids in video_ids:
        if ids[0] == '-':
            continue
        track = subprocess.check_output("youtube-dl --get-filename -o '%(track)s' {}".format(ids),shell=True,text=True)
        artist = subprocess.check_output("youtube-dl --get-filename -o '%(artist)s' {}".format(ids),shell=True,text=True)
        
        if track != 'NA\n' and artist !='NA\n':
            print("collecting uri of track : {} , artist: {}".format(track[0:-1],artist[0:-1]))
            # Tracks.append(track[:-1])
            # Artists.append(artist[:-1])
            uri = get_spotify_uri(track[0:-1],artist[0:-1])
            if uri != None:
                Uris.append(uri)
        
            


def create_playlist():

    request_body = json.dumps({
        "name": "WannabeCoder",
        "description": "G0Corona_CoronaG0",
        "public": False
    })

    url = 'https://api.spotify.com/v1/users/{}/playlists'.format(spotify_user_id)
    headers = {
        "Authorization" : "Bearer {}".format(spotify_Oauth_Token),
        'Accept': 'application/json'
    }

    response = requests.post(url, headers=headers, data=request_body)

    return response.json()['id']
    


def get_spotify_uri(song_name,song_artist):
    
    url = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=1".format(song_name,song_artist)

    headers = {
        "Authorization" : "Bearer {}".format(spotify_Oauth_Token),
        'Accept': 'application/json'
    }

    response = requests.get(url,headers=headers)
    print(song_name)
    # jprint(response.json())
    if len(response.json()['tracks']['items']):
        return response.json()['tracks']['items'][0].get('uri')



def add_song_to_playlist():

    # here we have to collect uris from get_spotify_uri() 
    uris = json.dumps({"uris": Uris})

    playlist_id = create_playlist()

    url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)
    headers = {
        "Authorization" : "Bearer {}".format(spotify_Oauth_Token),
        'Accept': 'application/json'
    }

    response = requests.post(url,headers=headers , data = uris)

    if response.status_code==201:
        print("Your PlayList is Created!!!")
    


if __name__ == '__main__':
    get_liked_videos()
    print(Uris)
    add_song_to_playlist()
    # Uris.append(get_spotify_uri("yummy","justin"))
    # Uris.append(get_spotify_uri("Shots (Album Version (Edited))","LMFAO"))
    # print()
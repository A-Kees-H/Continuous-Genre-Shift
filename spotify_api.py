import spotipy
import json
import time
import pprint
from collections import Counter
from random import choice
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

pprint = pprint.pprint
#https://spotipy.readthedocs.io/en/2.19.0/?highlight=current_user_saved_tracks#spotipy.client.Spotify.current_user_saved_tracks

#devices = {"iPhone":"ididid"} #for example

excluded_playlists = [
'spotify:playlist:6sg6XdSsLSRUrwFqZIGuch',
'spotify:playlist:1r3Ex7UmRTTJfuLWLSADZT',
'spotify:playlist:4jyeXFAubfvQTJuwKNB5pt',
'spotify:playlist:2x7twOhlbA2kPgLFgfgmHS',
'spotify:playlist:0Nfd1i1ofRRIXN8Kyk5ms1',
'Your Top Songs 2020',
'spotify:playlist:4jw2FokJh9eEUrLAQ4dltN',
'Liked from Radio',
'Your Top Songs 2021',
]

scope = """user-read-recently-played,
user-read-private,
user-read-email,
user-follow-modify,
user-follow-read,
user-top-read,
user-library-read,
user-library-modify,
playlist-modify-private,
playlist-read-private,
playlist-read-collaborative,
playlist-modify-public,
user-read-playback-state,
user-modify-playback-state,
user-read-currently-playing,
user-read-playback-position,
app-remote-control,
streaming,
ugc-image-upload"""



def get_artist_albums(artist_code):
    artist_uri = f'spotify:artist:{artist_code}'
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials("53b020dd9f9a4251af8515eb9705252f", "78287e7cf94e48f6be49760a9889366b"))

    results = sp.artist_albums(artist_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])

    for album in albums:
        print(album['name'])


def get_all(func, real_limit=999999999):
    results = func(limit=50)
    all_results = results["items"]
    offset = 0
    while results:
        offset += 50
        results = func(offset=offset, limit=50)["items"]
        all_results += results
        if len(all_results) > real_limit:
            all_results[0:real_limit]
            break
    #print(len(all_results))
    return all_results


def print_all_songs(results):
    for idx, item in enumerate(results):
        track = item['track']
        print(idx + 1, track['artists'][0]['name'], " – ", track['name'])


def print_all_liked():
    results = get_all(sp.current_user_saved_tracks)
    print_all_songs(results)


def print_recent(limit=25):
    pprint(get_recent(limit=limit))
    #print_all_songs(results)

def get_recent(limit=25):
    results = sp.current_user_recently_played(limit=limit)["items"]
    #pprint(results)
    songs = [(result["track"]["name"], [artist["name"] for artist in result["track"]["album"]["artists"]], result["track"]["album"]["name"], result["track"]["uri"]) for result in results]
    return songs

def get_recent_uris(limit=25):
    return [recent[3] for recent in get_recent(limit=limit)]

def print_recent_uris(limit=25):
    pprint(get_recent_uris(limit=limit))

def print_songs_from_playlist(uri):
    pprint(get_songs_from_playlist(uri))

def get_songs_from_playlist(uri):
    results = sp.playlist_tracks(uri)["items"]
    return [(result["track"]["name"], [artist["name"] for artist in result["track"]["album"]["artists"]][0], result["track"]["album"]["name"], result["track"]["uri"]) for result in results]

def get_uris_from_playlist(playlist):
    results = sp.playlist_tracks(playlist["uri"])["items"]
    uris = [result["track"]["uri"] for result in results]
    return uris


def print_all_albums():
    results = get_all(sp.current_user_saved_albums)
    for idx, item in enumerate(results):
        track = item['album']
        print(idx + 1, track['artists'][0]['name'], " – ", track['name'])

def get_playback():
    curr = sp.current_playback()
    return curr

def print_playback():
    print(get_playback())

def next_song():
    if get_playback():
        sp.next_track()
        print_playback()
    else:
        print("--- nothing to skip ---")

def previous_song():
    if get_playback():
        sp.previous_track()
        print_playback()
    else:
        print("--- nothing is playing ---")

def pause(device_id=None):
    if get_playback():
        pause_playback(device_id=device_id)
    else:
        print("--- nothing to pause ---")

def track_to_repeat():
    if get_playback():
        sp.repeat("track")
    else:
        print("--- nothing to repeat ---")

def album_or_playlist_to_repeat():
    if get_playback():
        sp.repeat("context")
    else:
        print("--- nothing to repeat ---")

def choose_position_in_track(pos):
    if get_playback():
        seek_track(pos)
    else:
        print("--- nothing playing ---")

def toggle_shuffle(io):
    sp.shuffle(io)

def play_on_diff_device(device_name):
    transfer_playback(devices[device_name])

def get_user_playlist_uris():
    ps = get_all(sp.current_user_playlists)
    uris = [a["uri"]  for a in ps]
    #names = [a["name"] for a in ps]
    return uris

def get_user_playlists():
    ps = get_all(sp.current_user_playlists)
    playlists = [{"name" : a["name"], 
                    "uri"  : a["uri"]}  for a in ps]
    #names = [a["name"] for a in ps]
    return playlists

def print_playlists():
    pprint([pl["name"] for pl in get_user_playlists()])

def play_song(uris, device_id=None):
    #print(device_id)
    if type(uris) == str:
        sp.start_playback(uris=[uris], device_id=device_id)
    elif type(uris) == list or type(uris) == tuple:
        sp.start_playback(uris=uris, device_id=device_id)

def queue_song(uri, device_id=None):
    sp.add_to_queue(uri, device_id=device_id)

def set_volume(vol):
    #0-100
    sp.volume(vol)


def play_album_or_playlist(uri, device_id=None):
    sp.start_playback(uri, device_id=device_id)  

def choose_random():
    uri = rand_choice(list(song_uri_db.keys()))
    print(song_uri_db[uri]["playlists"])
    return uri

def get_devices():
    """ Gets devices of a user
    """
    return sp._get("me/player/devices")["devices"]

def get_track_info(id_):
    #print(id_)
    id_ = id_.split(":")[2]
    #print(id_)
    return sp._get(f"tracks/{id_}")

def play(uris, device_id=None):
    if "playlist" in uris or "album" in uris:
        play_album_or_playlist(uri, device_id=device_id)
    else:
        play_song(uris, device_id=device_id)

def get_device_ids():
    return [device["id"] for device in get_devices()]

def print_devices():
    pprint([(device["name"], device["id"]) for device in get_devices()])

def get_song_library():
    playlists = get_user_playlists()
    playlists = [pl for pl in playlists if pl["name"] not in excluded_playlists and pl["uri"] not in excluded_playlists]
    song_db = []
    for playlist_uri in playlists:
        song_db += [(song_uri, playlist_uri) for song_uri in get_uris_from_playlist(playlist_uri) if "local" not in song_uri]
    return song_db


def get_song_genres(song_uri):
    t_info = get_track_info(song_uri)
    a_info = sp.artist(t_info["artists"][0]["uri"]) 
    genres = a_info["genres"]
    return genres


def get_dbs():
    song_db = get_song_library()
    genre_db = {}
    uri_db = [song[0] for song in song_db]
    counts = Counter(uri_db)
    songs = {}
    with_pl = []
    for song_uri in counts.keys():
        if song_uri not in songs.keys():
            genres = get_song_genres(song_uri)
            ind = 0
            playlists = []
            for i in range(counts[song_uri]):
                ind = uri_db.index(song_uri, ind)
                playlists.append(song_db[ind][1])
                ind += 1
            songs[song_uri] = {"genres":genres, "playlists":playlists}
    all_genres = {}
    for song_uri in songs.keys():
        genres = songs[song_uri]["genres"]
        for genre in genres:
            if genre not in all_genres.keys():
                all_genres[genre] = [song_uri]
            else:
                if song_uri not in all_genres[genre]:
                    all_genres[genre].append(song_uri)
    playlists = {}
    for playlist in get_user_playlists():
        playlists[playlist["uri"]] = get_uris_from_playlist(playlist)
    return songs, all_genres, playlists
        

def build_and_dump_json():
    song_db = get_dbs()
    song_db_w_date = {"date" : time.time(), "data" : song_db}
    json.dump(song_db_w_date, open("song_db.json", "w"))
    return song_db

def play_random_recent(device_id=None):
    play(rand_choice(get_recent_uris()), device_id=device_id)

def play_random_all(device_id=None):
    play(choose_random(), device_id=device_id)

def queue_random_all(device_id=None):
    queue_song(choose_random(), device_id=device_id)

def get_follow_on(uri):
    history = get_recent_uris()
    genres = song_uri_db[uri]["genres"]
    #print(genres)
    playlists = song_uri_db[uri]["playlists"]
    #print(playlists)
    pot_follows = [] #potential follow-on songs
    for playlist in playlists:
        pot_follows += playlist_db[playlist["uri"]]
    for genre in genres:
        pot_follows += genre_db[genre]
    pot_follows = [pot for pot in pot_follows if pot not in history]
    if not pot_follows:
        return ""
    else:
        return rand_choice(pot_follows)


def continuous_genre_shift():
    history = get_recent_uris(limit=50)
    while get_playback():
        time.sleep(15)
        uri = get_playback()["item"]["uri"]
        next_uri = get_follow_on(uri)
        add_to_queue(next_uri)



rand_choice = choice
sp = spotipy.Spotify(auth_manager=SpotifyOAuth("53b020dd9f9a4251af8515eb9705252f", "78287e7cf94e48f6be49760a9889366b", "http://silver-fin.org", scope=scope))

devices = get_device_ids()

try:
    song_db_w_date = json.load(open("song_db.json", "r"))
    #song_search_db
    song_db = song_db_w_date["data"]
    playlist_db = song_db[2]
    genre_db = song_db[1]
    song_uri_db = song_db[0]
    read_date = song_db_w_date["date"]
    if time.time() - read_date > 60 * 24 * 60:
        build_and_dump_json()
except FileNotFoundError:
    song_db = build_and_dump_json()

try:
    play_history = json.load(open("play_history.json", "r"))
except FileNotFoundError:
    play_history = []
    json.dump([], open("play_history.json", "w"))

"""
recommendation_genre_seeds()
recommendations()
"""
#play_random_all(device_id=devices[0])
#queue_random_all(device_id=devices[0])



TESTING = False

if TESTING:
    print_all_liked()
    print_all_albums()
    print_recent(40)
    print_playback()
    get_user_playlist_uris()
    print_playlists()


#print_devices()
#print_playlists()

#play_history = load(open("play_history.json" "r"))
#print_playlists()
def play_x(x):
    ##########################
    #use last uri in queueueueueu
    ######################
    uris = []
    #
    if not get_playback():
        new = True
        uri = rand_choice(list(song_uri_db.keys()))
    else:
        new = False
        uri = get_playback()["item"]["uri"]
    for i in range(x):
        uris.append(uri)
        next_uri = get_follow_on(uri)
        a = 0
        while next_uri in uris:
            a += 1
            if a > 6:
                print("no valid follow on found")
            next_uri = get_follow_on(uri)
        #print(get_track_info(next_uri)["name"])
        uri = next_uri
    pprint(uris)
    if new:
        play(uris)
    else:
        for uri in uris[1:]:
            queue_song(uri)


#next_song()

play_x(5)

#continuous_genre_shift()



print("\n\n\n\n\n\n\n\n")
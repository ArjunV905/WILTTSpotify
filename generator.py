import spotipy
from spotipy.oauth2 import SpotifyOAuth #SpotifyClientCredentials
import os
import sys

#----------------------------------[Fields]---------------------------------------------
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888'
cacheFolder = os.path.join(sys.path[0], ".cache")

# For printing colored text
def strRed(str): return("\033[91m {}\033[00m".format(str))
def strGreen(str): return("\033[92m {}\033[00m".format(str))
def strYellow(str): return("\033[93m {}\033[00m".format(str))
def strCyan(str): return("\033[96m {}\033[00m".format(str))

#----------------------------------[Methods]--------------------------------------------
# Read ClientID and ClientSecret from config.txt
def readCreds() -> bool:
    file = open(os.path.join(sys.path[0], "config.txt"), 'r')
    fileList = file.readlines()

    # Reading Client ID
    idLine = fileList[0]
    readID = ""
    inQuotes = False

    #       Searching through the line to find the Client ID
    for c in range(len(idLine)):
        if (not inQuotes and idLine[c] == "\""):
            inQuotes = True
        elif (inQuotes and idLine[c] != "\""):
            readID += idLine[c]
        elif (inQuotes and idLine[c] == "\""):
            inQuotes = False
    
    os.environ['SPOTIPY_CLIENT_ID'] = readID


    # Reading Client Secret
    secretLine = fileList[1]
    readSecret = ""
    inQuotes = False

    #       Searching through the line to find the Client Secret
    for c in range(len(secretLine)):
        if (not inQuotes and secretLine[c] == "\""):
            inQuotes = True
        elif (inQuotes and secretLine[c] != "\""):
            readSecret += secretLine[c]
        elif (inQuotes and secretLine[c] == "\""):
            inQuotes = False
    
    os.environ['SPOTIPY_CLIENT_SECRET'] = readSecret
    file.close()

    if (len(readID) > 0 and len(readSecret) > 0):
        return True

    return False


#---------------------------------------------------------------------------------------









#------------------------------------[Main]---------------------------------------------
# Checking if the credentials have been stored
if (not readCreds()):
    print(strRed("Error: Could not read credentials from config.txt"))
    input("Press Enter to exit...")
    sys.exit()

# Using the credentials to create a spotipy object
scope = 'playlist-modify-private'
cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=cacheFolder)
auth_manager = SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'], client_secret=os.environ['SPOTIPY_CLIENT_SECRET'], cache_handler=cache_handler, scope=scope)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Ensuring valid credentials were obtained
try:
    username = sp.current_user()['id']
    print("\nSuccessfully logged in as: ")
    print("\t" + strCyan(username) + "\n")
except spotipy.oauth2.SpotifyOauthError:
    print(strRed("Error: Could not authenticated with Spotify, please ensure that valid credentials are stored in config.txt"))
    input("Press Enter to exit...")
    sys.exit()


playlist = "https://open.spotify.com/playlist/6rcoePgRt6SaPQ3uKZdAKo?si=f270993300624a31"

results = sp.search(q='artist:Sabai', type='track')
items = results['tracks']['items']
for i, t in enumerate(items):
    print("%d %s" % (i + 1, t['name']))
    print(items[i]['id'])
    print(items[i]['uri'] + "\n")

    # Testing playlist adding
    sp.playlist_add_items(playlist, [items[i]['uri']], position=None)
    print(strGreen("Added \"" + t['name'] +"\" to playlist \n"))


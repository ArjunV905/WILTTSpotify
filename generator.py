import spotipy
from spotipy.oauth2 import SpotifyOAuth #SpotifyClientCredentials
import os
import sys

#----------------------------------[Fields]---------------------------------------------
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888'
cacheFolder = os.path.join(sys.path[0], ".cache")

# For printing colored text
def prRed(prt): print("\033[91m {}\033[00m" .format(prt))
def prGreen(prt): print("\033[92m {}\033[00m" .format(prt))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))

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
    prRed("Error: Could not read credentials from config.txt")
    input("Press Enter to exit...")
    sys.exit()

# Using the credentials to create a spotipy object
cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=cacheFolder)
auth_manager = SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'], client_secret=os.environ['SPOTIPY_CLIENT_SECRET'], cache_handler=cache_handler)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Ensuring valid credentials were obtained
try:
    username = sp.current_user()['id']
    prGreen("Successfully logged in as: ")
    prYellow("\t" + username + "\n")
except spotipy.oauth2.SpotifyOauthError:
    prRed("Error: Could not log in")
    input("Press Enter to exit...")
    sys.exit()



results = sp.search(q='artist:Sabai', type='track')
items = results['tracks']['items']
for i, t in enumerate(items):
    print("%d %s" % (i + 1, t['name']))
    print(items[i]['id'])
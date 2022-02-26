import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import sys
import datetime

#----------------------------------[Fields]---------------------------------------------
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888'
cacheFolder = os.path.join(sys.path[0], ".cache")

playlistTitle = "What I'm Listening to Today"

playlist = ""
numAdded = 0
numFailed = 0
#numDupes = 0

#----------------------------------[Methods]--------------------------------------------
# For printing colored text
def strRed(str): return("\033[91m {}\033[00m".format(str))
def strGreen(str): return("\033[92m {}\033[00m".format(str))
def strYellow(str): return("\033[93m {}\033[00m".format(str))
def strCyan(str): return("\033[96m {}\033[00m".format(str))

#---------------------------------------------------------------------------------------
# Read ClientID and ClientSecret from config.txt
def readCreds() -> bool:
    print("\nAttempting to read credentials from config.txt...")
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
# Read the playlist url from the config.txt file
def readPlaylist() -> bool:
    print("Checking if there is a playlist URL in config.txt...")
    file = open(os.path.join(sys.path[0], "config.txt"), 'r')
    fileList = file.readlines()

    # Reading playlist url
    playlistLine = fileList[2]
    readPlaylist = ""
    inQuotes = False

    #       Searching through the line to find the playlist url
    for c in range(len(playlistLine)):
        if (not inQuotes and playlistLine[c] == "\""):
            inQuotes = True
        elif (inQuotes and playlistLine[c] != "\""):
            readPlaylist += playlistLine[c]
        elif (inQuotes and playlistLine[c] == "\""):
            inQuotes = False

    global playlist
    playlist = readPlaylist
    file.close()

    if (len(playlist) > 0):
        return True

    return False


#---------------------------------------------------------------------------------------
# Using the credentials to authenticate and create a spotipy object
def authenticate():
    scope = "playlist-modify-public"
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=cacheFolder)
    auth_manager = SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'], client_secret=os.environ['SPOTIPY_CLIENT_SECRET'], cache_handler=cache_handler, scope=scope)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    return sp

#---------------------------------------------------------------------------------------
# Handles searching for the semester's playlist, and creates it if it doesn't exist
def playlistHandler():
    # Determines the semester appropriate playlist name
    titleHead = playlistTitle

    today = datetime.datetime.now()
    if (today.month < 7):
        semester = "Spring"
    else:
        semester = "Fall"
    playlistFullName = titleHead + " (" + semester + " " + str(today.year) + ")"

    # Searches for the playlist
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if (playlist['name'] == playlistFullName):
            print("Found pre-existing playlist: " + strCyan(playlistFullName) + "\n")
            return playlist['id']

    # If the playlist doesn't exist, create it
    print("Old playlist not found for " + semester + " " + str(today.year) + ", Creating new playlist titled: " + playlistFullName)
    newPlaylist = sp.user_playlist_create(username, playlistFullName, public=True)
    print("Successfully created new playlist: " + strCyan(newPlaylist['name']) + "\n")
    return newPlaylist['id']



#------------------------------------[Main]---------------------------------------------
# Checking if the credentials have been stored
if (not readCreds()):
    print(strRed("Error: Could not read/find credentials from config.txt"))
    input("Press Enter to exit...")
    sys.exit()

sp = authenticate()

# Ensuring valid credentials were obtained
try:
    username = sp.current_user()['id']
    print("Successfully logged in as: ")
    print("\t" + strCyan(username) + "\n")
except spotipy.oauth2.SpotifyOauthError:
    print(strRed("Error: Could not authenticate with Spotify, please ensure that valid credentials are stored in config.txt"))
    input("Press Enter to exit...")
    sys.exit()

# Determining if the stored playlist url is valid
defaultPlaylist = True

if (readPlaylist()):
    print("Checking if the playlist URL is valid...")
    try:
        playlistVals = sp.user_playlist(username, playlist)
        print(strGreen("\nSuccessfully loaded playlist: "))
        print("\t" + strCyan(playlistVals['name']) + "\n")
        defaultPlaylist = False
    except spotipy.client.SpotifyException:
        print(strRed("Error: Invalid playlist: ") + playlist)
        print("Skipping playlist override and continuing with default playlist...\n")

# Obtains the playlist link to add to from playlistHandler()
if (defaultPlaylist):
    playlist = playlistHandler()

# Reading the csv file




results = sp.search(q='artist:Sabai', type='track')
items = results['tracks']['items']
for i, t in enumerate(items):
    print("%d %s" % (i + 1, t['name']))
    print(items[i]['uri'] + "\n")

    # Testing playlist adding
    sp.playlist_add_items(playlist, [items[i]['uri']], position=None)
    print(strGreen("Added \"" + t['name'] +"\" to playlist \n"))


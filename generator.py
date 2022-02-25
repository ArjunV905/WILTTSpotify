import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import sys

#----------------------------------[Fields]---------------------------------------------
#os.environ['SPOTIPY_CLIENT_ID'] = '7e7e604745fa44c5a27798804efaadd8'
#os.environ['SPOTIPY_CLIENT_SECRET'] = 'cbb4ccc76a344180bfd92fbd0fee6d70'

# For printing colored text
def prRed(prt): print("\033[91m {}\033[00m" .format(prt))
def prGreen(prt): print("\033[92m {}\033[00m" .format(prt))

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
if (not readCreds()):
    prRed("Error: Could not read credentials from config.txt")
    input("Press Enter to exit...")
    sys.exit()

# Using the credentials to create a spotipy object
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=os.environ['SPOTIPY_CLIENT_ID'], client_secret=os.environ['SPOTIPY_CLIENT_SECRET']))
print("Successfully authenticated with Spotify...")



results = sp.search(q='artist:Sabai', type='track')
items = results['tracks']['items']
for i, t in enumerate(items):
    print("%d %s" % (i, t['name']))
    print(items[i]['id'])
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import sys
import datetime

#----------------------------------[Fields]---------------------------------------------
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888'
os.system("")  # To enable ansii escape characters in the terminal

playlistTitle = "What I'm Listening to Today"

playlist = ""
csvFilesLst = []
linesRead = 0

addedLines = []
failedLines = []
dupeLines = []
uncertainLines = []

songTitleCol = 3 # Column number in the .csv file - 1
artistCol = 4
linkCol = 5

addSuccessStr = ""
failedHeadStr = ""
dupeHeadSpStr = ""
dupeHeadLocalStr = ""
mismatchHeadStr = ""
#----------------------------------[Methods]--------------------------------------------
# Checks if the program is running as a script or frozen executable and sets the path accordingly
def setPath():
    if getattr(sys, 'frozen', False):
        bundleDir = os.path.dirname(sys.executable)
    else:
        bundleDir = sys.path[0]

    return bundleDir

#---------------------------------------------------------------------------------------
# For printing colored text
def strRed(str): return("\033[91m{}\033[00m".format(str))
def strGreen(str): return("\033[92m{}\033[00m".format(str))
def strYellow(str): return("\033[93m{}\033[00m".format(str))
def strCyan(str): return("\033[96m{}\033[00m".format(str))

#---------------------------------------------------------------------------------------
# Removes ", ', and \n from the string
def textCleaner(str):
    newStr = str.replace("\"", "")
    newStr = newStr.replace("\'", "")
    newStr = newStr.replace("\n", "")
    return newStr

#---------------------------------------------------------------------------------------
# Removes any color characters from the string
def removeColorChars(str):
    str = str.replace("\033[91m", "") # Red
    str = str.replace("\033[92m", "") # Green
    str = str.replace("\033[93m", "") # Yellow
    str = str.replace("\033[96m", "") # Cyan

    str = str.replace("\033[00m", "") # Reset

    return str

#---------------------------------------------------------------------------------------
# Read ClientID and ClientSecret from config.txt
def readCreds() -> bool:
    print("\nAttempting to read credentials from config.txt...")
    try:
        #file = open(os.path.join(sys.path[0], "config.txt"), 'r')
        file = open(os.path.join(bundleDir, "config.txt"), 'r')
    except FileNotFoundError as e:
        print(strRed("\nError: config.txt not found."))
        print(e)
        input("Press enter to exit...")
        sys.exit()
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
    file = open(os.path.join(bundleDir, "config.txt"), 'r')
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
# Reads all of the .csv files and returns an array of the lines read
def readCSV():
    global linesRead
    global csvFilesLst

    print("\nReading all .csv files in the folder...")
    csvFiles = os.listdir(bundleDir)
    csvList = []

    for file in csvFiles:
        if (file.endswith(".csv")):
            csvList.append(file)

    csvList.sort()
    csvList.reverse()

    # Check if csvList is empty
    if (len(csvList) == 0):
        print(strRed("No .csv files found!"))
        input("Press enter to exit...")
        sys.exit()

    # Adding all of the lines from the .csv files to an array
    csvLines = []
    for file in csvList:
        print("Reading file: " + strCyan(file))
        csvFile = open(os.path.join(bundleDir, file), 'r')

        # Removes the first line (header) from being stored
        csvFile.readline()

        # Loop through the rest of the lines in the .csv file and add them to the array
        while True:
            line = csvFile.readline()
            if not line: break
            csvLines.append(line)
            linesRead += 1


        #csvLines.append(csvFile.readlines())
        csvFile.close()

    print("\nRead " + strCyan(str(len(csvList))) + " .csv files.\n")
    csvFilesLst = csvList
    return csvLines

#---------------------------------------------------------------------------------------
# Filter out the csv file input to contain either a spotify link or artist and song name
def filterCSV(csvLines):
    global songTitleCol
    global artistCol
    global linkCol
    
    filteredCSV = []
    for line in csvLines:
        # Split lines by comma
        line = line.split(",")

        # Checking if the line in linkCol is a spotify link
        if (line[linkCol].startswith("https://open.spotify.com/track/")):
            filteredCSV.append(spotifyURL_ID(line[linkCol]))
        else:
            # Using the artist and song name to search for a spotify link
            filteredCSV.append(findSpotifyID(textCleaner(line[artistCol]), textCleaner(line[songTitleCol])))
    

    return filteredCSV

#---------------------------------------------------------------------------------------
# Returns the spotify id from the input url
def spotifyURL_ID(url):
    # Removing the "https://open.spotify.com/track/" from the url
    url = url.replace("https://open.spotify.com/track/", "")

    # Removing the "?" from the url
    url = url[:url.find("?")]

    return url

#---------------------------------------------------------------------------------------
# Finds a spotify ID from the artist and song name
def findSpotifyID(artist, song) -> str:
    global failedHeadStr

    # Searching for a spotify ID
    resultStr = ""
    results = sp.search(q='artist:' + artist + ' track:' + song, type='track')

    # If no results are found, output a warning
    if (results['tracks']['items'] == []):
        failedHeadStr = "No results found for Song: "
        outputLine = strRed(failedHeadStr) + strCyan(song) + strRed(" by ") + strCyan(artist)
        print(outputLine)
        failedLines.append(outputLine)
        return "-1"

    # If multiple results are found, add anyway 
    if (len(results['tracks']['items']) > 1):
        # Adding the first result
        resultStr = results['tracks']['items'][0]['id']
        print(strYellow("Found song: ") + strCyan(results['tracks']['items'][0]['name']) + (" by ") + strCyan(results['tracks']['items'][0]['artists'][0]['name']))
    else:   # Single spotify ID found [Appears that spotify never gives a single result]
        resultStr = results['tracks']['items'][0]['id']

    # Checks if there is uncertianity in the result
    compareNames(artist, song, results)
    # If a single result is found, return the spotify ID
    return resultStr

#---------------------------------------------------------------------------------------
# Compares the read artist and song name with the names from the Spotify query (Returns true if they match)
def compareNames(artist, song, results):
    global mismatchHeadStr
    # Compare the lowercase artist and song name with the lowercase artist and song name from the Spotify query
    if (artist.lower() == results['tracks']['items'][0]['artists'][0]['name'].lower() and song.lower() == results['tracks']['items'][0]['name'].lower()):
        return True
    else:
        mismatchHeadStr = "Mismatch in names found for "
        message = strYellow(mismatchHeadStr + "Input: ") + strCyan(song) + strYellow(" by ") + strCyan(artist) + strYellow(" \n\tand Spotify Song: ") + strCyan(results['tracks']['items'][0]['name']) + (" by ") + strCyan(results['tracks']['items'][0]['artists'][0]['name'])
        #print(message)
        uncertainLines.append(message)
        return False

#---------------------------------------------------------------------------------------
# Checks all the read IDs to remove any duplicates
def removeDuplicates(filteredCSV):
    global dupeHeadLocalStr
    print("\nChecking for duplicate IDs from the csv file...")
    for i in range(len(filteredCSV)):
        for j in range(i + 1, len(filteredCSV)):
            if (filteredCSV[i] == filteredCSV[j] and filteredCSV[i] != "-1"):
                spotTrack = sp.track(filteredCSV[i])
                dupeHeadLocalStr = "Duplicate found in csv file: "
                message = strYellow(dupeHeadLocalStr) + strCyan(spotTrack['name']) + strYellow(" by ") + strCyan(spotTrack['artists'][0]['name'])
                print(message)
                dupeLines.append(message)
                filteredCSV[i] = "-1"
    
    print("\n")
    return filteredCSV

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
    print("\nSuccessfully created new playlist: " + strCyan(newPlaylist['name']) + "\n")
    return newPlaylist['id']


#---------------------------------------------------------------------------------------
# Checks if the playlist already contains the song
def isDupe(link, playlistTracks):
    global dupeHeadSpStr
    # Checks if the playlist is empty 
    if (sp.playlist(playlist)['tracks']['total'] == 0):
        return False

    # Checks if the playlist already contains the song
    for track in playlistTracks['items']:
        # Compare the tracks by id
        if (track['track']['id'] == sp.track(link)['id']):
            dupeHeadSpStr = "Duplicate found in Spotify playlist: "
            dupeLine = strYellow(dupeHeadSpStr) + strCyan(track['track']['name']) + strYellow(" by ") + strCyan(track['track']['artists'][0]['name'])
            print(dupeLine)
            dupeLines.append(dupeLine)
            print("Skipping track...")
            return True

    return False

#---------------------------------------------------------------------------------------
# Creates a log file containing playlist modification info in the log folder
def createLogFile():
    global csvFilesLst

    print("\nCreating log file...")

    # Create the log folder if it doesn't exist
    if not os.path.exists(os.path.join(bundleDir, "logs")):
        os.makedirs(os.path.join(bundleDir, "logs"))
    
    # Create the log file based on the os path
    logFileName = str(datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + "-log.txt"
    logFilePath = os.path.join(bundleDir, "logs", logFileName)
    logFile = open(logFilePath, "w+")

    # Writing the headers
    logFile.write("User ID: " + username + "\n")
    logFile.write("Playlist: " + sp.user_playlist(username, playlist)['name'] + "\n")
    
    # Write the csv files that were read
    logFile.write("\n.csv Files Read:\n")
    for file in csvFilesLst:
        logFile.write("\t" + file + "\n")

    # Write the song additions
    if (len(addedLines) > 0):  
        logFile.write("\nAdded Songs:\n")
        for line in addedLines:
            line = line.replace(addSuccessStr, "")
            logFile.write("\t" + removeColorChars(line) + "\n")

    # Write the failed songs
    if (len(failedLines) > 0):
        logFile.write("\nFailed Songs:\n")
        for line in failedLines:
            line = line.replace(failedHeadStr, "")
            logFile.write("\t" + removeColorChars(line) + "\n")

    # Write the duplicate songs
    if (len(dupeLines) > 0):
        logFile.write("\nDuplicate Songs:\n")
        for line in dupeLines:
            line = line.replace(dupeHeadSpStr, "")
            line = line.replace(dupeHeadLocalStr, "")
            logFile.write("\t" + removeColorChars(line) + "\n")

    # Write the uncertain songs
    if (len(uncertainLines) > 0):
        logFile.write("\nUncertain Songs:\n")
        for line in uncertainLines:
            line = line.replace(mismatchHeadStr, "")
            logFile.write("\t" + removeColorChars(line) + "\n\n")
    
    # Write the summary line 
    logFile.write("\nSummary:\n")
    logFile.write(str(linesRead) + " songs read from file(s)\n")
    logFile.write(str(len(addedLines)) + " songs added\n")
    logFile.write(str(len(dupeLines)) + " duplicate songs\n")
    logFile.write(str(len(failedLines)) + " songs failed\n")
    logFile.write(str(len(uncertainLines)) + " uncertain songs\n")
    logFile.write(str(len(csvFilesLst)) + " csv files read\n")

    logFile.close()
    print("Log file successfully created as: " + strCyan(logFileName))
    

#------------------------------------[Main]---------------------------------------------
bundleDir = setPath()
cacheFolder = os.path.join(bundleDir, ".cache")

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
csvLines = readCSV()
filtered = filterCSV(csvLines)
finalIDs = removeDuplicates(filtered)

# Add the spotify links to the playlist
# When adding, if value is -1, skip the line
allTracks = sp.playlist_tracks(playlist)    # Avoiding the need to re-query the playlist
for link in finalIDs:
    if (link != "-1" and isDupe(link, allTracks) == False):
        sp.user_playlist_add_tracks(username, playlist, [link])
        addSuccessStr = "Successfully added song: "
        message = strGreen(addSuccessStr) + strCyan(sp.track(link)['name']) + strGreen(" by ") + strCyan(sp.artist(sp.track(link)['artists'][0]['id'])['name'])
        print(message)
        addedLines.append(message)

# ______________________
# Summary output section
print("-------------------------------------------[Summary]-------------------------------------------")

#   [Duplicate Lines]
if (len(dupeLines) > 0):   
    for dupe in dupeLines:
        print(dupe)

#   [Uncertain Lines]
if (len(uncertainLines) > 0):
    print("\n")
    for uncertain in uncertainLines:
        print(uncertain)
    print("NOTE: The above mismatches have been added to the playlist (Unless they were duplicates)")
    print("\n")

#   [Failed Lines]
if (len(failedLines) > 0):
    for failed in failedLines:
        print(failed)

#   [User and Playlist Info]
print("\n")
playlistTypeStr = "default"
if (not defaultPlaylist):
    playlistTypeStr = "overridden"

print("Added to " + strCyan(sp.current_user()['display_name']) + "'s " + playlistTypeStr + " playlist: " + strCyan(sp.user_playlist(username, playlist)['name']))

#   [Values]
print("Lines read: " + str(linesRead) + "\tLines added: " + strGreen(str(len(addedLines))) + "\tDuplicate lines: " + strYellow(str(len(dupeLines))) + "\tFailed lines: " + strRed(str(len(failedLines))))

#   [Log file]
if (linesRead > 0):
    # Calling log file creation function
    createLogFile()
    # Print statement


input("\nPress Enter to exit...")
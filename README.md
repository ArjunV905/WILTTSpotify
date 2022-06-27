# WILTTSpotify

Generates a Spotify playlist with songs read from a csv file

## Usage

This program was intended for a specific Music college course, but can also be used for other purposes

The program will read through csv files which contain the name, artist, and a link to a song and accordingly add them to a playlist titled "What I'm Listening to Today" followed by the current semester and year. An override playlist can instead be used to skip this procedure and add the read songs into this override playlist. 

A log in the format of a text file will be created in the logs directory within the project folder, which will specify the songs added, duplicate songs, failed songs, and the songs with mismatching names.

You will require setting up a Spotify developer account, 
provide the config.txt file a link to the playlist you want to add to, and modifying the generator.py file to indicate which columns contain the song name, artist, and link in the csv file(s).

## Setup

#### Dependencies
You will require ``Python3, Git, Spotipy``

Spotipy can be installed through pip
```
pip install spotipy
```

#### Downloading
First, download the project using GitHub's "Download Zip" option or by using 
```
git clone https://github.com/ArjunV905/WILTTSpotify
```

#### Setting up a Spotify Developer account and App
To set up your Spotify developer account, head to https://developer.spotify.com/dashboard/login and login with a 
regular Spotify account. 

After logging in, press the "Create An App" button and name the app according to the purpose of the bot (such as "csvToPlaylist")

Then, you need to go to "Edit Settings" in your new app and under the "Redirect URIs" section, add `http://localhost:8888`to it.

You can now copy your Client ID and Client Secret from your app's dashboard page and paste them into the config.txt file.

## Executing the Program

Running the program through the `generator.py` file
```
python3 generator.py
```

You will be promped to log in to Spotify and authorize the app upon your first use. Make sure to use the same Spotify account you have used to create the Developer account. 

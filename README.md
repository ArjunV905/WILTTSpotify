# WISTTSpotify

Generates a Spotify playlist with songs read from a csv file

## Usage

This program was intended for a specific Music college course, but can also be used for other purposes

You will require setting up a Spotify developer account and 
need to provide the config.txt file a link to the playlist you want to add to.

## Setup

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

# Next Update - June/July 2026
- Improve queue display with better formatting and pagination
- Soundcloud, deezer, tidal, apple music support
- Add queue search functionality
- Add queue shuffle functionality
- Add queue repeat functionality
- Add previous song skip functionality
- Add queue priority management
- Add queue sorting functionality
- Add user to user music DJ system (?)
- Add favourite songs/albums saving
- Add playlist creation and management (?)
----------
## MAKE SURE YOU UPDATE DISCORD.PY TO USE THE NEW DAVE PROTOCOL OR IT WON'T WORK: `pip install -U discord.py[voice]`
## Update Log 
### v1.3 (Current) - April 2nd 2026
- Added a `clear` command to clear the queue
- Improved queue management and user experience
- Added queue loop functionality
- Added support for **youtube playlists** `[limited to 50 tracks, but you can change this in the code]`
- Started queue priority management
<img width="668" height="351" alt="loop" src="https://github.com/user-attachments/assets/f73b9d54-2785-4418-a4e3-f6c8eed5cb30" />
<img width="1339" height="41" alt="clearqueue" src="https://github.com/user-attachments/assets/163e009c-993c-4ebc-a062-6596a03c12fd" />
<img width="648" height="801" alt="youtubesupport" src="https://github.com/user-attachments/assets/f26efc05-4564-4360-8109-8fd0c4d53ab9" />

### [NOTE]: This is just a small update to combat the new issue where spotify requires users to have a premium subscription to use their APIs', hence the support for youtube playlists now, so you can use that instead for now until the next update.

----------
## Update Log
### v1.2 - January 5th 2026
- Added interactive help system with dropdown menu
- Added queue tracker
- Added `/queue` command to display current music queue
- Added `/help` to help lmao
- Fixed now playing embed updates between songs - accurate and automatic after a song finishes
- Added progress tracking for playlist processing
- Support for plain text YouTube searches
- Fixed URL length issues in embeds
- Updated branding to Division Interactive


### v1.1 (30/11/24)
- Embed / Buttons
- Queue glitch bug fix where you can only skip a song once even though there are multiple song(s) in the queue. You may now add BULK playlists on spotify and it will be streamed through in batches of 5 at a go.
- Fetch YT thumbnail and other dope stuff ig
- Support for immediate playback of huge playlists
- Youtube playback support (pushed next update icba)
- Dropdown to view different pages, queue [SOON] and [DJ system? SOON] A


<img width="931" height="877" alt="image" src="https://github.com/user-attachments/assets/0e1d59a7-fed4-41cc-9a41-99a85971acb7" />


https://divisionbot.space/
---------

# Spotify Discord
Made this for my server, but you can use it too ig lmao
Uses spotipy library to fetch spotify track/album info and uses ytdlp to extract audio and stream it directly through discord 

# Get started
> 1) Download FFMPEG
> This is a required prerequisite (all credits to [@DanielOrourke02](https://github.com/DanielOrourke02) for bringing this up and suggesting a resolve - woulda forgot). Using this because it supports far more formats and is better in quality. Check the link to see how to get started with FFMPEG:  https://transloadit.com/devtips/how-to-install-ffmpeg-on-windows-a-complete-guide/

> 2) Download dependencies:
> **Unless you're a complete idiot, this should be easy..**
```python
pip install discord
pip install spotipy
pip install yt-dlp
pip install pynacl
```

> 3) Get spotify API scopes:
> Scopes needed: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` [in cogs/music.py] - these can be obtained [here](https://developer.spotify.com/dashboard)

> 4) Start your bot:
> Add your bot token and start it, this required slash commands

I'll be regularly updating this, current version v1.1, v1.2 will be pushed soon, request fixes/features on pull req and i'll update this with features by the 10th

Open a pull request to request bug fixes blah blah

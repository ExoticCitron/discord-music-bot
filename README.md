# Next Update - February 2026
- Focus on improving queue management and user experience
- Add a `clear` command to clear the queue
- Improve queue display with better formatting and pagination
- Add queue search functionality
- Add queue shuffle functionality
- Add queue repeat functionality
- Add previous song skip functionality
- Add queue loop functionality
- Add queue priority management
- Add queue sorting functionality
- Add user to user music DJ system (?)
- Add favourite songs/albums saving
- Add playlist creation and management (?)
----------
## Update Log
### v1.2 (Current) - January 5th 2026
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


![Screenshot 2024-11-24 182914](https://github.com/user-attachments/assets/a8841c72-58fe-4b15-9e14-4db7a0cc1a20)


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

# Will be updated on Decemeber 2025

###### I would like to note, this is a start of my school A-Level coding project, I am required to code something to hand in, this will be it. I may or may not maintain this in the future. As of right now, there will be frequent updates til i'm 17 (next year) XD
----------
## Update v1.1 NOW LIVE (30/11/24)
###### Next Update v1.2 (around christmas) - request features on pull request and/or fixes, ill update this readme with update features by the 10th of dec 
 
Features (current v1.1):
- Embed / Buttons
- Queue glitch bug fix where you can only skip a song once even though there are multiple song(s) in the queue. You may now add BULK playlists on spotify and it will be streamed through in batches of 5 at a go.
- Fetch YT thumbnail and other dope stuff ig
- Support for immediate playback of huge playlists
- Youtube playback support (pushed next update icba)
- Dropdown to view different pages, queue [SOON] and [DJ system? SOON]


![Screenshot 2024-11-24 182914](https://github.com/user-attachments/assets/a8841c72-58fe-4b15-9e14-4db7a0cc1a20)


https://exo-devs.tech/
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
```

> 3) Get spotify API scopes:
> Scopes needed: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` [in cogs/music.py] - these can be obtained [here](https://developer.spotify.com/dashboard)

> 4) Start your bot:
> Add your bot token and start it, this required slash commands

I'll be regularly updating this, current version v1.1, v1.2 will be pushed soon, request fixes/features on pull req and i'll update this with features by the 10th

Open a pull request to request bug fixes blah blah

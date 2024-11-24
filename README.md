## Future Update v1.1
- Embed / Buttons
- Queue glitch bug fix where you can only skip a song once even though there are multiple song(s) in the queue | the fixes will be pushed around next month so look out for a tona bug patches / embed/button styles
- Fetch YT thumbnail and other dope stuff ig
- Support for immediate playback of huge playlists
- Youtube playback support
- Dropdown to view different pages, queue and [DJ system?]

![Screenshot 2024-11-24 122650](https://github.com/user-attachments/assets/8e2c16f6-244e-4c60-86a2-f3bafb1c8bee)


https://exo-devs.tech/
---------

# Spotify Discord
Made this for my server, but you can use it too ig lmao
Uses spotipy library to fetch spotify track/album info and uses ytdlp to extract audio and stream it directly through discord 

# Get started
> 1) Download FFMPEG
> This is a required prerequisite (all credits to [@DanielOrourke02](https://github.com/DanielOrourke02 for bringing this up and suggesting a resolve - woulda forgot). Using this because it supports far more formats and is better in quality. Check thie link to see how to get started with FFMPEG:  https://transloadit.com/devtips/how-to-install-ffmpeg-on-windows-a-complete-guide/

> 2) Download dependencies:
> **Unless you're a complete idiot, this should be easy..**
```python
pip install discord
pip install spotipy
pip install yt-dlp
```

> 3) Get spotify API scopes:
> Scopes needed: `client_id`, `client_secret` - these can be obtained [here](https://developer.spotify.com/dashboard)

> 4) Start your bot:
> Add your bot token and start it, this required slash commands

I'll be regularly updating this, current version v1.0 has a tonna queue bugs because it's stored in a dict and its only for small servers, this will be fixed as we progress on latter versions. Next commit around next monthish with embeds/buttons and bug fixes and db updates ig

Open a pull request to request bug fixes blah blah

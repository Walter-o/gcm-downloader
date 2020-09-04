# gcm-downloader
Groove coaster mobile server downloader

yes, to run this you need to have python 3 installed and 
install dependencies by putting these lines in your command prompt or shell:
```batch
pip install pycryptodome
pip install bs4
pip install requests
```
after that you can run start.py and achieve server files yes.

What does it download:

- .Pak files (contains filenames of server assets and game assets)
- .m4a previews (Basically the preview songs you'd hear in the ingame song before purchasing a song)
- .ogg music (Every song (BGM+SHOT) in the game including DLC and removed songs)
- chart files (They include leveldata and filenames of the .mp3 so the program does parse them at util.getNamesFromChart())

What it can't download yet:

- Ads (The ad banners you can see at login page and in store, i have working code for this but i'll implement it into this project cleanly later)
- Titles (The title-cards you can select as a player, again, i have working code, i'll implement soon)
- All .pak files (The server still stores older pak files that could contain removed songs, will implement the option to use this later)

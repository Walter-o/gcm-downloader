# gcm-downloader
**Groove coaster mobile server downloader**

![photoshopped](https://user-images.githubusercontent.com/33218378/92583339-7af14280-f292-11ea-83a0-dfd2f57b48ca.png)

yes, to run this you need to have python 3 installed and 
install dependencies by double-clicking `start.bat`
after that you can start but if you want to start it faster you can do
```batch
python start.py
```
or if you for example want to do mode 1 and 2 you can do:
```batch
python start.py 12
```
and achieve server files yes.

**What does it download:**

- .pak files (contains filenames of server assets and game assets)
- .ogg music (Every song (BGM+SHOT) in the game including DLC and removed songs)
- .dat charts (They include filenames of the .ogg music so the program does parse them at util.getNamesFromChart())
- .dat chart revisions (Some charts have a bug fixed or changed, these revision charts will also be downloaded)
- .m4a previews (Basically the preview songs you'd hear ingame before purchasing a song)
- Ads (The ad banners you can see at login page and in store)
- Titles (The title-cards you can select as a player)
- All .pak files (It contains a bruteforced list of all links up until 2020/09/09)

**Bro what is the password:**

All .zip files are encrypted by default with **`eiprblFFv69R83J5`**, i don't want to alter the data.
If you forget it somehow, you can find it again in util.ZIP_PASSWORD

for hardcore archivists i recommend:
```batch
python start.py 1234
```
since that downloads everything this program can download (about 8.55 GB as of 2020/09/09)

Disclaimer, colored command prompt thumbnail may or may not be photoshopped.

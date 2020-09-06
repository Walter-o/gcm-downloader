from multiprocessing import Pool
import os

import util

# Download newest paks and returns dict of their names
# This also returns stageParamData from newest tuneFile pak
def downloadNewPaks(soup):
    paks = {
        "tunePak": soup.find("tunefile_pak").find("url").text,
        "modelPak": soup.find("model_pak").find("url").text,
        "skinPak": soup.find("skin_pak").find("url").text
    }
    [util.downloadIfNotExists(url) for url in paks.values()]

# Scans every tuneFile.pak and chart file present in data folder for more data, yes
def downloadRecursive():
    pass

# Downloads pre-bruteforced paks from server
def downloadOldPaks():
    pass

# Downloads all updated chart data
def downloadChartUpdateData(soup):
    pass

# Downloads all music previews
def downloadPreviews(stageParamData):
    previewNames = util.getNamesFromStageTEMP(stageParamData, search=b"_sample", includes=7)
    [util.downloadIfNotExists(util.sampleUrl % previewName)
     for previewName in previewNames]

# Downloads all chart data
def downloadChartData(stageParamData):
    stageNames = util.getNamesFromStageTEMP(stageParamData, search=b"\x64\x64", includes=0)
    [util.downloadIfNotExists(util.stageUrl % stageName)
     for stageName in stageNames]

# Downloads all music files
def downloadMusic():
    stageFolder = util.convertPath("ios/gc2/stage")
    for stageFilename in os.listdir(stageFolder):
        names = [name
                 for datData in util.getDatsFromZip(os.path.join(stageFolder, stageFilename))
                 for name in util.getNamesFromChart(datData)
                 if not name.lower().endswith(("_hard", "_normal", "_easy", "_h", "_n", "_e"))]
        names = list(dict.fromkeys(names))  # Removes duplicates
        [util.downloadIfNotExists(util.musicUrl % name)
         for name in names]

# Downloads all player title images, (bruteforce)
def downloadTitles():
    pass

# Downloads all advertisement banner images
def downloadAds():
    pass


# TODO TunePreferences.xml somhow contains all names for overwrite songs
#      Find out where they come from EDIT1: probably start.php

def main(mode):
    # Get BeautifulSoup object of start.php
    # Download new pak files from start.php
    # Open stageparam.dat from tuneFile.pak
    # Load the 404 urls list from 404.json
    soup = util.getStartPhpSoup()
    downloadNewPaks(soup=soup)
    stageParamData = util.openStageParam(soup=soup)
    util.reload404List()

    if mode >= 1:
        downloadPreviews(stageParamData=stageParamData)
        downloadChartData(stageParamData=stageParamData)
        #downloadChartUpdateData(soup=soup)
        downloadMusic()
    if mode >= 2:
        downloadTitles()
        downloadAds()
    if mode >= 3:
        downloadOldPaks()
    if mode >= 4:
        downloadRecursive()

def CLI():
    print("Groove Coaster server downloader by Walter\n" + "-" * 20)
    print("Hello! What would you like to do")
    print("1 = Just download all gameplay files we're missing")
    #print("2 = ^^ + title cards and ad banners")
    #print("3 = ^^ + downloading many old pak files")
    #print("4 = ^^ + scanning those pak files for stuff too")
    while True:
        choice = input("> ")
        if choice.isdigit() and int(choice) in range(1, 4+1):
            main(mode=int(choice))
            print("Enjoy your files!")
            break
        else:
            print("PLS provide number ok?")

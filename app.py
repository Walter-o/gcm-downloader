import multiprocessing
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
    [util.downloadIfNotExists(url, bruteForce=False) for url in paks.values()]

# Scans every tuneFile.pak and chart file present in data folder for more data, yes
def downloadRecursive():
    pass

# Downloads pre-bruteforced paks from server
def downloadOldPaks():
    pass

# Downloads all updated chart data
def downloadChartUpdateData(soup):
    # Documentation on these
    # Looks like these are chart *Updates* that the server instructs the
    # client to update these files with these revisions. They are given
    # by start.php and stored in the client inside TunePreferences.xml
    stagePaks = soup.find_all("stage_pak")
    stageNames = [stagePak.find("name").text + stagePak.find("date").text
        for stagePak in stagePaks]
    [util.downloadIfNotExists(util.stageUrl % stageName, bruteForce=False)
     for stageName in stageNames]

# Downloads all music previews
def downloadPreviews(stageParamData):
    previewNames = util.getNamesFromStageTEMP(stageParamData, search=b"_sample", includes=7)
    [util.downloadIfNotExists(util.sampleUrl % previewName, bruteForce=False)
     for previewName in previewNames]

# Downloads all chart data
def downloadChartData(stageParamData):
    stageNames = util.getNamesFromStageTEMP(stageParamData, search=b"\x64\x64", includes=0)
    [util.downloadIfNotExists(util.stageUrl % stageName, bruteForce=False)
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
        [util.downloadIfNotExists(util.musicUrl % name, bruteForce=False)
         for name in names]

# Downloads all player title images, (bruteforce)
def downloadTitles():
    titleUrls = [
        util.titleUrl % "t%04d%04d_e.png" % (title, variation)
        for title in range(0, 100 + 1)  # 24 was last title as of 2019/10/25
        for variation in range(0, 200 + 1)  # Highest variation was 78
    ]
    print("Alright we're bruteforcing %s title urls" % len(titleUrls))
    with multiprocessing.Pool(processes=50) as pool:
        pool.map(util.downloadIfNotExists, titleUrls)


# Downloads all advertisement banner images
def downloadAds():
    dates = util.dateRange(2015, util.datetime.now().year)
    links = [
        url % date + leadChar + language + fileType
        for date in dates
        for leadChar in util.leadChars
        for language in util.languages
        for fileType in util.fileTypes
        for url in [util.infoAdUrl, util.coverFlowAdUrl]
    ]
    print("Ok now we bruteforce %s ad urls" % len(links))
    with multiprocessing.Pool(processes=50) as pool:
        pool.map(util.downloadIfNotExists, links)

def main(mode):
    # Get BeautifulSoup object of start.php
    # Download new pak files from start.php
    # Open stageparam.dat from tuneFile.pak
    soup = util.getStartPhpSoup()
    downloadNewPaks(soup=soup)
    stageParamData = util.openStageParam(soup=soup)

    if mode == 0:
        downloadAds()
    if mode == 1:
        downloadPreviews(stageParamData=stageParamData)
        downloadChartData(stageParamData=stageParamData)
        downloadChartUpdateData(soup=soup)
        downloadMusic()
    if mode == 2:
        downloadTitles()
        downloadAds()
    if mode == 3:
        downloadOldPaks()
    if mode == 4:
        downloadRecursive()


def CLI():
    print("\n" * 50)
    print("Groove Coaster server downloader by Walter")
    print("-" * 20)
    print("Hello! What would you like to do")
    print("1 = Just download all gameplay files we're missing")
    print("2 = Bruteforce title cards and ad banners")
    #print("3 = Download many old pak files")
    #print("4 = Scanning every old pak file in /data/ for downloads")
    while True:
        choice = input("> ")
        if choice.isdigit() and int(choice) in range(0, 4+1):
            main(mode=int(choice))
            print("Enjoy your files!")
            break
        else:
            print("PLS provide number ok?")
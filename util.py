# A Private project by Walter
# A Weapon to surpass Crypto Coaster

from urllib.parse import urlencode, urlparse
from datetime import timedelta, datetime
from Crypto.Cipher import AES
from bs4 import BeautifulSoup
import requests
import zipfile
import json
import os

# Found in: mtxc::ObbFile::getZipPassword()
# Used for: Crypting zip files containing audio, chart data and .obb file
ZIP_PASSWORD = b"eiprblFFv69R83J5"

# Found in: aesManager::initialize()
# Used for: Crypting parameter bytes sent by client
AES_CBC_KEY = b"oLxvgCJjMzYijWIldgKLpUx5qhUhguP1"

# Found in: aesManager::decryptCBC() and aesManager::encryptCBC()
# Used for: Crypting parameter bytes sent by client
AES_CBC_IV = b"6NrjyFU04IO9j9Yo"

# Base parameters for doing requests to php
baseParams = {
    "os": "android",
    "os_ver": "9",
    "tid": "020000000000",
    "vid": "65a2f74c649b4e8c85f1f43273f287cd2f1b46a3d2474050a37f0b81cd847241",
    "sid": "d143d4873dd9b987722c94560c13e4599a52c43de6c4658135d2b5737c718d9a",
    "lang": "en",
    "ver": "2.0.10"
}

startUrl = "http://gc2018.gczero.com/start.php"
musicUrl = "http://dl.sp-taitostation.com/ios/gc2/ogg/%s.ogg.zip"
stageUrl = "http://dl.sp-taitostation.com/ios/gc2/stage/%s.zip"
sampleUrl = "http://dl.sp-taitostation.com/ios/gc2/m4a/%s_sample.m4a"
pakUrl = "http://dl.sp-taitostation.com/ios/gc2/%s"
titleUrl = "http://gc2018.gczero.com/img/title/%s"
infoAdUrl = "http://gc2018.gczero.com/img/info/Info/%s"
coverFlowAdUrl = "http://gc2018.gczero.com/img/web_shop/cover_flow/%s"

absPath = os.path.dirname(os.path.abspath(__file__))
json404Path = os.path.join(absPath, "404.json")

global list404 # List containing all 404'd urls

# Lists for bruteforcing Ads
leadChars = ["a", "b", "c", "d", "e", "f", "g", "TOUHOU"]
fileTypes = [".jpg", ".gif", ".png"]
languages = ["_EN", "_JP", ""]

# Turns a bytes object into an integer
def hexint(bytesObj):
    return int("0x" + bytesObj.hex(), 16) if type(bytesObj) != int else bytesObj

# Extracts all music filenames from given .dat data inside stage .dat files, NOTE don't give ext files
def getNamesFromChart(datData):
    marker = b"\x3f"  # 4 bytes after this 3F in infosize is where first wordLength starts
    null = b"\x00"  # If there are more words then we get a 00 otherwise something else
    wordsList = []
    infoSize = hexint(datData[6:8])  # TODO We can only load first 8 bytes and determine how much data we need to load
    datData = datData[:infoSize]  # Crop file
    markerPos = datData.rfind(marker)
    if markerPos == -1:
        raise Exception("marker not found")
    wordStart = markerPos + len(marker) + 4
    cursor = wordStart
    while True:
        lenByte = datData[cursor]
        cursor += 1
        wordLength = lenByte
        word = datData[cursor:cursor + wordLength]
        cursor += wordLength
        nullByte = datData[cursor:cursor + 1]
        cursor += 1
        wordsList.append(word.decode("utf-8"))
        if nullByte != null:
            break
    if len(wordsList) != 4:
        print("bugged wordlist")
        print("wordsList", wordsList)
        print("infoSize", infoSize)
        print("wordStart", wordStart)
        print("markerPos", markerPos)
        print("data", datData)
        raise Exception("Words list was not size of 4")
    return wordsList

# Gets all music names from stage_param.dat
def getNamesFromStage(datData):
    # TODO fix this garbage soon
    pass

# Gets all music names from stage_param.dat (temporarily solution)
def getNamesFromStageTEMP(datData, search, includes=0):
    """
    Yes i know this code is garbage and i should optimize it
    but there might not be much time left
    i'll improve it soon after the program is done

    includes = how many bytes of search variable are
               included in the filename

    searches are [
    \x64\x64 for stage names, includes = 0
    _sample for preview names, includes = 7
    ]
    """

    # Pops number of bytes to hexint from pakFile
    def take(bytesAmount):
        nonlocal datData, cursor
        taken = datData[cursor:cursor + bytesAmount]
        cursor += bytesAmount
        return hexint(taken)

    cursor = 0
    fileCount = take(2)
    datData = datData
    searchCount = datData.count(search)

    """
    Our approach here is to find every entry of _normal
    and backtrack each byte until we find one that matches
    the length of the filename we have at the moment which is
    the nameLength byte, from there we can crop out the file name
    """ # TODO Sample names are seperate too, this function only stage names we cant use unless lucky per file
    names = []
    while True:
        index = datData.find(search)
        if index == -1:
            break
        # If our match overlaps (particularly with \x64\x64) then index += 1
        if datData[index + 2] == search[0]:
            index += 1
            searchCount -= 1

        for i in range(64):
            byte = datData[index - i]
            if byte == (i - 1 + includes):
                name = datData[index - i + 1: index]
                if len(name) != 0:
                    names.append(name.decode("utf-8"))
                break
        datData = datData[index + len(search):]

    print("Extracted [%s / %s] matches of %s" % (len(names), searchCount, str(search)))
    # Chrono is the only one not following the standard
    # luckily the id is same for music, chart and sample so this should do
    # Daddy because dd is our search
    return names + ["bbchrono", "daddy"]

# Decrypts given pak file and returns list of files
def decryptPak(pakFile, onlyFiles=None):
    # Credits to Luigi Auriemma on ZenHAX for writing the bms script this function is based upon
    # But not only that, his tutorials on zenhax.com have immensely helped me with
    # decryption in this project and in the future many to come. Respect!

    # Pops number of bytes to hexint from pakFile
    def take(bytesAmount):
        nonlocal pakFile, cursor
        taken = pakFile[cursor:cursor + bytesAmount]
        cursor += bytesAmount
        return hexint(taken)

    cursor = 0
    pakSize = take(4)  # Size of entire file
    infoSize = take(4)
    infoSize = take(4)  # Twice size of info area, bruh these dudes are high
    zero = take(1)  # 0 to indicate stop of header
    globalNamesOffset = cursor
    baseOff = cursor + infoSize
    files = take(2)
    array = {i:{
            "nameOffset": take(4),
            "offset": take(4),
            "size": take(4),
            "zero": take(1)
        } for i in range(files)}
    # We need a final word start so we know the end for the last word
    array[files] = {"nameOffset": take(4)}
    outFiles = {}
    for i in range(files):
        nameOffset = array[i]["nameOffset"]
        offset = array[i]["offset"]
        size = array[i]["size"]
        nameSize = array[i+1]["nameOffset"] - nameOffset
        nameOffset += globalNamesOffset
        offset += baseOff
        name = pakFile[nameOffset:nameOffset + nameSize].decode("utf-8")
        if onlyFiles is not None and name in onlyFiles:
            file = pakFile[offset: offset + size]
            outFiles[name] = file
    return outFiles

# Decrypt AES encrypted data, takes in a hex string
def decryptAES(data, key=AES_CBC_KEY, iv=AES_CBC_IV):
    return AES.new(key, AES.MODE_CBC, iv).decrypt(bytes.fromhex(data))

# Encrypt data with AES, takes in a bytes object
def encryptAES(data, key=AES_CBC_KEY, iv=AES_CBC_IV):
    # i cant, im tired and i can't wrap my mind around this spaghetti abomination of security
    while len(data) % 16 != 0:
        data += b"\x00"
    encryptedData = AES.new(key, AES.MODE_CBC, iv).encrypt(data)
    return encryptedData.hex()

# Encode parameter data in the cringe style taito does
def encodeParams(dictionary):
    # Cringe, their own trademark breaking format and : inside registration_id
    return bytes(urlencode(dictionary, safe=":") + "&(C)TAITOCORP2013", encoding="utf-8")

# Makes a request to the server
def serverRequest(url, updateParams=None):
    params = baseParams
    if updateParams is not None: params.update(updateParams)
    params = encodeParams(params)
    encryptedParams = "?" + encryptAES(params)
    r = requests.get(url + encryptedParams,
                     headers={"User-Agent": "Apache-HttpClient/UNAVAILABLE (java 1.4)"})
    return r

# Downloads given file
def download(url, bruteForce=True):
    if url in list404 and not bruteForce:
        return
    try:
        if not bruteForce:
            print("Downloading %s " % url, end="")
        r = requests.get(url)
        if r.ok:
            print("OK")
            with open(convertPath(urlparse(url).path), "wb") as outFile:
                outFile.write(r.content)
        elif r.status_code == 404:
            if not bruteForce:
                print("404 banning...")
                append404List([url])
            return
        else:
            print("FAIL", r.status_code)
            return download(url)
    except Exception as error:
        print("Error at download(%s): %s" % (url, error))
        return download(url)

# Download given file if it doesn't exist already
def downloadIfNotExists(url, **kwargs):
    filename = os.path.basename(url)
    folderName = os.path.dirname(convertPath(urlparse(url).path))
    if not os.path.exists(folderName):
        os.makedirs(folderName)
    if filename not in os.listdir(folderName):
        download(url, **kwargs)

# Gives local file location when you give relative server path
def convertPath(serverPath):
    return os.path.join(absPath, "data", serverPath.strip("/"))

# Gives all usable .dat file contents from given stage .zip filename
def getDatsFromZip(stageZipName):
    z = zipfile.ZipFile(stageZipName)
    z.setpassword(ZIP_PASSWORD)
    wantedFiles = [filename for filename in z.namelist()
                   if not filename.endswith("_ext.dat") and filename.endswith(".dat")]
    datDatas = []
    for filename in wantedFiles:
        with z.open(filename, "r") as datFile:
            datDatas.append(datFile.read())
    return datDatas

# Opens stageparam.dat from newest tuneFile.pak
def openStageParam(soup):
    tuneFilePath = convertPath(urlparse(soup.find("tunefile_pak").find("url").text).path)
    with open(os.path.join(absPath, "data", tuneFilePath), "rb") as tuneFile:
        tuneFile = tuneFile.read()
    stageParamData = decryptPak(tuneFile, onlyFiles=["stage_param.dat"])["stage_param.dat"]
    return stageParamData

# Returns BeautifulSoup object of start.php
def getStartPhpSoup():
    r = serverRequest(startUrl)
    if r.ok:
        return BeautifulSoup(r.text, "lxml")
    else:
        raise Exception("Got statuscode %s for getStartPhpSoup()" % r.status_code)

# Returns a list of dates between 2 given years,
# e.g: 2019, 2020 returns 20190101 - 20201231
def dateRange(sYear, eYear):
    date = datetime(sYear, 1, 1)
    day = timedelta(days=1)
    dates = []
    while True:
        dates.append("%04d%02d%02d" % (date.year, date.month, date.day))
        date += day
        if date.year > eYear: break
    return dates

# Takes in a pak name and a single date entry from dateRange()
# and returns all possible pak names for that date
def generatePakNames(pakName, date):
    return [pakName + date + "%02d%02d.pak" % (h, m)
            for h in range(0, 24)
            for m in range(0, 60)]

# Loads the 404 urls list and creates it if it doesn't exist
def load404List():
    if not os.path.exists(json404Path):
        with open(json404Path, "w") as init404:
            json.dump({"404":[]}, init404)
    with open(json404Path, "r") as json404Read:
        return json.load(json404Read)["404"]

# Appends given list to the 404 urls list
def append404List(list404):
    with open(json404Path, "r") as json404Read:
        json404Read = json.load(json404Read)["404"]
    with open(json404Path, "w") as json404Append:
        json.dump({"404": json404Read + list404}, json404Append)

# Reloads the 404 list that contains bad urls
def reload404List():
    global list404
    list404 = load404List()

reload404List()
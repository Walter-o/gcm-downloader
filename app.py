import os

import util

# Updates all data from server to us
def update():
    # Update pak files and load stage_param.dat from tuneFile.pak
    tuneFilePath = util.convertPath(util.urlparse(util.getNewPakUrls()["tunePak"]).path)
    with open(os.path.join(util.absPath, "data", tuneFilePath), "rb") as tuneFile:
        tuneFile = tuneFile.read()
    stageParamData = util.decryptPak(tuneFile, onlyFiles=["stage_param.dat"])["stage_param.dat"]

    # Download all chart data
    stageNames = util.getNamesFromStageTEMP(stageParamData, search=b"\x64\x64", includes=0)
    [util.downloadIfNotExists(util.stageUrl % stageName)
     for stageName in stageNames]

    # Download all music previews
    previewNames = util.getNamesFromStageTEMP(stageParamData, search=b"_sample", includes=7)
    [util.downloadIfNotExists(util.sampleUrl % previewName)
     for previewName in previewNames]

    # Download all music data
    stageFolder = util.convertPath("ios/gc2/stage")
    for stageFilename in os.listdir(stageFolder):
        names = [name
            for datData in util.getDatsFromZip(os.path.join(stageFolder, stageFilename))
            for name in util.getNamesFromChart(datData)]
        names = list(dict.fromkeys(names))  # Removes duplicates
        [util.downloadIfNotExists(util.musicUrl % name)
         for name in names
         if not name.lower().endswith(("_hard", "_normal", "_easy", "_h", "_n", "_e"))]

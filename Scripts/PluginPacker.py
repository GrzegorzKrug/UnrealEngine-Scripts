import os
import sys
import zipfile
import json
import traceback
import argparse


from datetime import datetime

# --- Sys Params ---
parser = argparse.ArgumentParser()
parser.add_argument("--ide", action="store_true")
parser.add_argument("--verbose", action="store_true")
args = parser.parse_args()

# --- CONFIGURATION ---
sourceFolder = os.path.dirname(__file__)
SEP = "= = =  " * 5


VERSIONS = [
    5,
    5.1,
    5.2,
    5.3,
    5.4,
    5.5,
    5.6    
]
VERSIONS += [-1]

EXT_WHITELIST = [
    "md",
    "cpp",
    "h",
    "cs",

    "uplugin",  # removed to custom packing solution
    "uasset",
    "umap",
    "uproject",
    "ini",

    "png",
    "jpg",
    "jpeg",
    "tga",
    "bmp",
    "gif",
    "exr",
    "hdr",
    "mp3",
    "wav",
    "ogg",
    "flac",
    "mat",
    "material",
    "usf",
    "ush",
    "anim",
    "fbx",
    "curve",
    "uc",
    "umaterial",
    "uanimation",
    "uanimsequence"
]

FILE_NAMES_BLACKLIST = [
    "copyright",
    "license",
    "readme",
]

FOLDER_BlackList = [
    "Binaries",
    "Build",
    "Intermediate",
    'test',
    ".vs",
    ".idea",
    "git"
]

SUBFOLDERS_WhiteList = [
    "content",
    "source",
    "resources",
    "documentation",
    "config",
]


def modifyUplugin(folderPath, *, packVersion=None, zipfp=None):
    files = [f for f in os.listdir(folderPath) if f.endswith('.uplugin')]
    print(files)
    if (len(files) != 1):
        raise ValueError(f"Not found uplugin file! Got: {files}")

    upluginPath = os.path.join(folderPath, files[0])
    with open(upluginPath, mode="rt")as fp:
        UpluginTxt = json.load(fp)

        if ("EngineVersion" not in UpluginTxt):
            raise KeyError("Not found Engine version!")

        version = [UpluginTxt['EngineVersion']]

        if packVersion is not None:
            packVersion = f"{float(packVersion):<1.01f}"
        print(f"Found version: {version}, changing to -> {packVersion}")

        # version += VERSIONS
        # for ver in version:
        # if packVersion is not None:
        UpluginTxt["EngineVersion"] = packVersion
        zipfp.writestr(os.path.basename(upluginPath),
                       json.dumps(UpluginTxt, indent=4))
        print(f"Writing uplugin to: {packVersion} / {upluginPath}")


def packFile(path, *, zipfp=None, projectMainDir=None):
    nameText = os.path.basename(path)
    temp = nameText.lower().split(".")
    if len(temp) >= 2:
        name, ext = temp[-2], temp[-1]
        ext = ext.lower()
    else:
        name = temp[0]
        ext = None
    name = name.lower()

    for bln in FILE_NAMES_BLACKLIST:
        if bln.lower() in name:
            print("\t-> Skip blacklisted:", nameText)
            return

    if ext is None:
        print(f"\t-> Skip no extensions: '{nameText}'")
        return

    # arcname= os.path.join(str(version), os.path.relpath(path, projectMainDir))
    arcname = os.path.relpath(path, projectMainDir)

    for wh in EXT_WHITELIST:
        wh = wh.strip()
        if wh.lower() in ext:
            break
    else:
        print("\t-> Skip file:", nameText)
        return

    if arcname in zipfp.namelist():
        print("\t-> Skip existing file: ", nameText)
        return

    # print(f"Relative path: {arcname}")
    print(f"\tPacking file: {os.path.basename(path)}")
    zipfp.write(path, arcname)
    # print(f"[{arcname}] Added: {arcname}")


def walkFolder(path, *, mainFolder=False, version=-1, zipfp=None, projectMainDir=None):
    folderName = os.path.basename(path)
    folderText = str(folderName).lower()
    # folderText: str

    if mainFolder:
        "For main folder only"
        if version > 0:
            modifyUplugin(path, packVersion=version, zipfp=zipfp)
            walkFolder(path, mainFolder=True, version=-1, zipfp=zipfp, projectMainDir=projectMainDir)
            return
        else:
            "Do not name check this folder"
            pass
    else:
        for black in FOLDER_BlackList:
            if black.lower() in folderText:
                print("-> Skipping folder(1):", folderName)
                return

        pathLower = path.lower()
        folders = pathLower.split(os.path.sep)
        for wh in SUBFOLDERS_WhiteList:
            if (wh.lower() in folders):
                # print("white subfolder: ", wh, pathLower)
                break
        else:
            print("-> Skipping folder(2):", folderName)
            return

    print(f"= Folder: {folderName}")

    # Two loops for depth readability in console.
    for some in os.listdir(path):
        newPath = os.path.join(path, some)
        if (os.path.isfile(newPath)):
            packFile(newPath, projectMainDir=projectMainDir, zipfp=zipfp)

    for some in os.listdir(path):
        newPath = os.path.join(path, some)
        if (os.path.isdir(newPath)):
            walkFolder(newPath, version=version, projectMainDir=projectMainDir, zipfp=zipfp)


def start(version):
    versionText = f"{float(version):<1.01f}"
    # --- PROCESS EACH PROJECT FOLDER ---
    for folderName in os.listdir(sourceFolder):
        projectMainDir = os.path.join(sourceFolder, folderName)
        if not os.path.isdir(projectMainDir):
            print(f"Skipping: {folderName}")
            continue

        print("\n" + SEP, ", ver: ", version)
        date_str = datetime.now().strftime("%Y%m%d-%H%M")
        if (version > 0):
            output_zip = f"{projectMainDir}_{date_str}_{versionText}.zip"
        else:
            output_zip = f"{projectMainDir}_{date_str}.zip"
        # output_zip = f"{projectMainDir}_test.zip"
        if (os.path.isfile(output_zip)):
            print(f"Removing old zip: {output_zip}")
            os.remove(output_zip)

        # ZIP_BZIP2
        # ZIP_DEFLATED # 12
        # ZIP_LZMA  # 14
        wasError = False
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_LZMA) as zipf:
            kwargs = dict(zipfp=zipf, projectMainDir=projectMainDir)
            try:
                walkFolder(projectMainDir, mainFolder=True, version=version, **kwargs)
            except Exception as err:
                print(f"Exception was caught:{err}")
                traceback.print_exc()
                wasError = True
        # print(f"Packing: {folderName}")
        if (wasError):
            os.remove(output_zip)
            print(f"Packing finished")
        else:
            print(f"Packing finished, created :'{folderName}'\n{output_zip}")
        print("--- " * 5)


if __name__ == "__main__":
    for ver in VERSIONS:
        start(ver)

    if not args.ide:
        input("Program has finished...")
    else:
        print("Program has finished...")

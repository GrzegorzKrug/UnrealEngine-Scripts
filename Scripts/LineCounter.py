import matplotlib.pyplot as plt
import numpy as np
import glob
from matplotlib.style import use
import os

use("ggplot")

MIN_LINES = 10

# EXACT CASE SENS
WHITEFOLDERS = [
    "Source",
    "Plugins"
]

# Case Insensitive
IGNOREFOLDERPATTERNS = [
    ".git",
    "git",
    "binaries",
    "Content",
    "x64",
    "saved",
    "deriv",
    "config",
    "cache",
    "debug",
    "gtest",
    "inter"
]

# NoCase Sens, No . Sens
FILETYPES = [
    ".cpp",
    ". h",
    ". py"
]

FILETYPES = [txt.lower().strip(" .") for txt in FILETYPES]


class LineParser:

    OutLines = dict()

    def CheckFile(self, path):
        if (os.path.isdir(path)):
            print(f"This is not file!!! {path}")
            return

        BaseName = os.path.basename(path)
        nameArr = BaseName.split(".")
        name = nameArr[0]
        if (len(nameArr) == 2):
            ext = nameArr[-1]
        else:
            # print(f"Unique extension for file: {nameArr}, at {path}")
            if (len(nameArr) > 2):
                ext = nameArr[-1]
            else:
                ext = ""
        if (ext not in FILETYPES):
            return

        outVal = self.ReadFile(path)
        print(f"File: {BaseName} has: {outVal} lines ")
        self.OutLines[path] = outVal

    def WalkThisFolder(self, path):
        Search = os.path.join(path, "*")
        folders = glob.glob(Search)
        print(f"\n===> Walking: {path}")
        for sub in folders:
            if os.path.isdir(sub):
                Lp.FolderChecker(sub)
            else:
                Lp.CheckFile(sub)

    def FolderChecker(self, path):
        basName = os.path.basename(path)
        basNameLower = basName.lower()

        if (os.path.isdir(path)):
            if (os.path.basename(path) in WHITEFOLDERS):
                # print(f"Valid folder: {basName}")
                self.WalkThisFolder(path)

            for ext in IGNOREFOLDERPATTERNS:
                ext = ext.lower()
                if ext in basNameLower:
                    return

            self.WalkThisFolder(path)
            # print(f"Valid folder2: {basName}")
        else:
            self.CheckFile(path)

    @staticmethod
    def ReadFile(path):
        linesTotal = 0
        blankTotal = 0
        shortLines = 0
        codeLines = 0
        comments = 0
        preprop = 0
        name = os.path.basename(path)
        with open(path, "rt")as fp:
            for line in fp:
                txt = line.strip(" \t\r\n")
                # print(len(line))
                # print(len(txt))
                if (len(txt) < 1):
                    # print(txt)
                    blankTotal += 1
                    continue

                txt = line.strip(" \n\t\r;")
                if (len(txt) <= 5
                        and (
                            ("}" in txt or ")" in txt or "{" in txt) or "(" in txt
                )):
                    shortLines += 1
                    # print(txt)
                elif (txt.startswith("#")):
                    preprop += 1
                elif (txt.startswith("//") or txt.startswith(r"/*") or txt.endswith(r"*/")):
                    comments += 1
                else:
                    codeLines += 1

                linesTotal += 1
        return blankTotal, shortLines, codeLines, comments, preprop


if __name__ == "__main__":
    INPUT_PATH = os.path.dirname(__file__)
    print(f"Reading: {INPUT_PATH}")
    Lp = LineParser()
    Lp.WalkThisFolder(INPUT_PATH)

    # a = dict()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    KEYS = []
    ResultArray = np.zeros((0, 5), dtype=int)
    X = []
    Y = []
    Z = []
    Cm = []
    B = []

    for file, vals in Lp.OutLines.items():
        if (file.endswith(".py")):
            continue

        if (np.sum(vals) <= MIN_LINES):
            print(F"FILE FEw LINES: {os.path.basename(file)}, {vals}")
            continue

        ResultArray = np.concatenate([ResultArray, [vals]])
        KEYS.append(file)
        X += [vals[0]]
        Y += [vals[1]]
        Z += [vals[2]]
        Cm += [vals[3]]
        B += [vals[4]]
        if (vals[2] > 300):
            x = vals[0] + vals[1]
            y = vals[3]
            z = vals[2]
            ax.text3D(x, y, z, os.path.basename(file), color=(0.7, 0, 0.3, 0.4))
    del Lp
    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)
    Cm = np.array(Cm)
    B = np.array(B)

    X = X + Y
    Y = Cm

    ax.scatter3D(X, Y, Z, marker="+", color=(0, 0, 0, 1))
    BackAlfa = 0.6
    ax.scatter3D(X.max(), Y, Z, marker='.', color=(0.5, 0, 0, BackAlfa))
    ax.scatter3D(X, Y.max(), Z, marker='.', color=(0, 0.5, 0, BackAlfa))
    ax.scatter3D(X, Y, Z * 0, marker='.', color=(0, 0, 0.5, BackAlfa))

    # print(Total)

    ax.set_xlim(X.min(), X.max() + 5)
    ax.set_ylim(Y.min(), Y.max() + 5)
    ax.set_zlim(Z.min(), Z.max() + 5)

    ax.set_xlabel("Blank Lines / Braces")
    ax.set_ylabel("Comments")
    ax.set_zlabel("Code lines")
    ax.view_init(elev=20, azim=360 - 135)

    Total = ResultArray.sum(0)
    plt.suptitle(
        f"Blank/Braces: {Total[0]+Total[1]}, Comments: {Total[3]}, Lines(Code): {Total[2]}. "
        f"Total: {Total.sum()}")
    plt.figure()

    TotalLinesPerFile = ResultArray.sum(1)
    SubCommentRatio = ResultArray[:, 2] / TotalLinesPerFile
    # print(SubCommentRatio.shape)
    RS = np.argsort(SubCommentRatio)
    print("\n =" * 5)
    # print(RS, RS.shape)
    print()

    SortedResults = ResultArray[RS, :]
    # SortedResults = ResultArray
    del TotalLinesPerFile
    PX = SortedResults[:, 2]
    PY = SortedResults[:, 3]
    PZ = SortedResults[:, 4]

    TotalLinesPerFile = SortedResults.sum(1).astype(int)
    # print(f"Dividor: {TotalPerFile}, {TotalPerFile.shape}")
    PX = PX / TotalLinesPerFile
    PY = PY / TotalLinesPerFile
    PZ = PZ / TotalLinesPerFile
    # print(ResultArray.shape)
    # print(SortedResults.shape)
    # print(Total.shape)

    for i, rs in enumerate(RS):
        key = KEYS[rs]
        name = os.path.basename(key)
        curVals = SortedResults[rs, :]
        # print(curVals)
        # print(curVals.shape)
        print(f"{rs:>3}, {name:<30s} "
              f"Blank:{curVals[0]:<3}, ():{curVals[1]:<3}, Code:{curVals[2]:<3}, "
              f"Comments:{curVals[3]:<3}, PreProcess:{curVals[4]:<3}")

    plt.plot(PX, label="CodeLines")
    plt.plot(PY, label="Comments")
    plt.plot(PZ, label="Preprocessor")

    plt.title("Relative ratio in each file")
    plt.legend(loc="best")
    plt.tight_layout()

    plt.show()

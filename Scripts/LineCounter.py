import matplotlib.pyplot as plt
import numpy as np
import glob

import os


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

        outDc = self.ReadFile(path)
        print(f"File: {BaseName} has: {outDc} lines ")
        self.OutLines[path] = outDc

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
        with open(path, "rt")as fp:
            for line in fp:
                txt = line.strip(" \t\r\n")
                # print(len(line))
                # print(len(txt))
                if (len(txt) < 1):
                    # print(txt)
                    blankTotal += 1
                    continue

                txt = line.strip(" \n\t\r/\\*;")
                if (len(txt) <= 5
                        and (
                            ("}" in txt or ")" in txt or "{" in txt) or "(" in txt
                )):
                    shortLines += 1
                    # print(txt)
                else:
                    codeLines += 1

                linesTotal += 1
        return blankTotal, shortLines, codeLines


if __name__ == "__main__":
    INPUT_PATH = os.path.dirname(__file__)
    print(f"Reading: {INPUT_PATH}")
    Lp = LineParser()
    Lp.WalkThisFolder(INPUT_PATH)

    # a = dict()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    Total = np.array([0, 0, 0])
    X = []
    Y = []
    Z = []
    for file, vals in Lp.OutLines.items():

        print(file, vals)
        # plt.scatter3d
        if (file.endswith(".py")):
            continue
        Total += vals
        X += [vals[0]]
        Y += [vals[1]]
        Z += [vals[2]]
        if (vals[2] > 300):
            ax.text3D(*vals, os.path.basename(file))

    ax.scatter3D(X, Y, Z)

    print(Total)

    ax.set_xlabel("Blank / New Lines")
    ax.set_ylabel("Lines With braces")
    ax.set_zlabel("Code")
    plt.suptitle(f"Total blank: {Total[0]}, LineBraces: {Total[1]}, Code lines: {Total[2]}")
    # plt.tight_layout()
    plt.show()

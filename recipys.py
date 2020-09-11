#!/usr/bin/python3

import re, sys, os, itertools, pathlib, shutil
from lang import *
from conf import *

def findFiles(regex, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if re.search(regex, name):
                result.append(os.path.join(root, name))
    return result

def categories(recipe_file):
    file = open(recipe_file, "r")
    temp = [match.group(1) for line in file if (match := re.search("\[//\]: # \((.+?)\)", line)) is not None]
    return sorted(temp)

def title(recipe_file):
    file = open(recipe_file, "r")
    for line in file:
        if (match := re.search("^## (.+)", line)) is not None:
            return match.group(1)

def hasCategories(recipe, categories):
    for c in categories:
        if not c in recipe[1]: return False
    return True

allRecipes = sorted([(title(r), categories(r), r.replace(RECIPEDIR, "", 1))
                     for r in findFiles(".*\.md", RECIPEDIR)])
allCategories = sorted(set([c for r in allRecipes for c in r[1]]))

def recipesWithCategories(categories):
    return [r for r in allRecipes if hasCategories(r, categories)]

def createCategoryCombinations():
    result = dict()
    for t, c, r in allRecipes:
        for i in range(len(c)+1):
            for comb in itertools.combinations(c, i):
                if comb in result:
                    result[comb].append((t, c, r))
                else:
                    result[comb] = [(t, c, r)]
    return result

def overviewFilename(categories):
    filename = "".join(categories) if len(categories) > 0 else "index"
    return filename + ".md"


# Create category combinations
allCC = createCategoryCombinations()

for cc in allCC:
    pathlib.Path(OVERVIEWDIR).mkdir(parents=True, exist_ok=True)
    file = open(OVERVIEWDIR + overviewFilename(cc), "w")
    file.write("# " + OVERVIEW_TITLE + "\n\n")
    if len(cc) > 0:
        file.write("##### " + DROP_CATEGORIES + "\n\n")
    for c in cc:
        file.write("- [" + c + "](" + overviewFilename([remains for remains in cc if remains != c]) + ")\n")
    
    file.write("\n##### " + PICK_CATEGORY + "\n\n")
    for c in allCategories:
        if c in cc: continue
        linkedCC = tuple(sorted(cc + (c, )))
        if linkedCC in allCC:
            file.write("- [" + c + "](" + overviewFilename(linkedCC) + ")\n")

    file.write("\n-------------------------\n\n")
    firstLetter = "0"
    for r in allCC[cc]:
        if r[0][0] != firstLetter:
            while r[0][0] != firstLetter:
                firstLetter = chr(ord(firstLetter) + 1)
            file.write("\n## " + firstLetter + "\n\n")
        file.write("- [" + r[0] + "](../" + r[2] + ")\n")
        
    file.close()

# Create index page
pathlib.Path(BUILDDIR + "docs/").mkdir(parents=True, exist_ok=True)
file = open(BUILDDIR + "docs/index.md", "w")
file.write("<head><meta http-equiv='refresh' content='0; URL=overview/index.html'></head>")
file.close()

# Create statistics page
file = open(BUILDDIR + "docs/statistics.md", "w")
file.write("# " + STATISTICS_TITLE + "\n\n")
file.write(STATISTICS_TEXT.format(N_recipes = len(allRecipes), N_categories = len(allCategories)))
file.close()

# Copy recipes
for r in allRecipes:
    dst = pathlib.Path(BUILDDIR + "/docs/" + r[2])
    dst.parents[0].mkdir(parents=True, exist_ok=True)
    shutil.copy(RECIPEDIR + r[2], dst)

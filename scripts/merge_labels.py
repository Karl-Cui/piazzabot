import os

from utils import load_pickle, save_pickle


root_folder = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03"
labeled_files = [
    "Labeler0-50",
    "Labeler50-100",
    "Labeler100-150",
    "Labeler150-200",

    "labeled_200-400",

    "Labeler400-450",
    "Labeler450-525",

    "labeled_525-end"
]

# format file names
labeled_files = [f + ".pkl" for f in labeled_files]
labeled_files = [os.path.join(root_folder, f) for f in labeled_files]

# load pickles
pickles = [load_pickle(f) for f in labeled_files]
pairs = sum(pickles, [])

# find groups of dupes by creating a mapping then using DFS to find groups
mapping = {}
dupes_set = set()

for a, b in pairs:
    dupes_set.add(a)
    dupes_set.add(b)

    if mapping.get(a) is None:
        mapping[a] = set()
    mapping[a].add(b)

    if mapping.get(b) is None:
        mapping[b] = set()
    mapping[b].add(a)

dupe_groups = []

while dupes_set:
    idx = dupes_set.pop()
    search = [idx]
    seen = {idx}

    while search:
        idx = search.pop()

        for dupe in mapping[idx]:
            if dupe not in seen:
                dupes_set.remove(dupe)
                search.append(dupe)
                seen.add(dupe)

    dupe_groups.append(seen)

# save
save_path = os.path.join(root_folder, "dupes.pkl")
save_pickle(dupe_groups, save_path)

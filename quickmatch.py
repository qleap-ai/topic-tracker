import nltk


def tokenize(text):
    word_list = nltk.word_tokenize(text.replace("-", " "))
    return [word.lower() for word in word_list if word.isalpha()]


def decompose_text(text):
    tokens = tokenize(text)
    candidates = []
    for i in range(0, len(tokens) - 1):
        cand = tokens[i]
        candidates.append(cand)
        for j in range(i + 1, min(i + 4, len(tokens))):
            cand = cand + '_' + tokens[j]
            candidates.append(cand)
    # print(str(len(tokens))+" "+str(len(candidates)))
    return candidates


def quick_match(text, mwe_set):
    candidates = decompose_text(text)
    matched_mwes = {}
    for cand in candidates:
        if cand in mwe_set:
            if cand in matched_mwes.keys():
                matched_mwes[cand] += 1
            else:
                matched_mwes[cand] = 1
    return matched_mwes



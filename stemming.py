prefixes = []
with open("korijenovanje/prefiksi.txt", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if line != "" and line[0] != "/" and line not in prefixes:
            prefixes.append(line)
prefixes.sort(key=len, reverse=True)

suffixes = []
with open("korijenovanje/sufiksi.txt", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if line != "" and line[0] != "/" and line not in suffixes:
            suffixes.append(line)
suffixes.sort(key=len, reverse=True)

def process_word(word):
    processed_word = word

    for prefix in prefixes:
        # if word.starswith(prefix) and word != prefix and len(word) > 2:
        if word.startswith(prefix) and word != prefix:
            processed_word = word.removeprefix(prefix)
            break

    for suffix in suffixes:
        # if word.endswith(suffix) and word != suffix and len(word) > 2:
        if word.endswith(suffix) and word != suffix:
            processed_word = word.removesuffix(suffix)

            if processed_word.endswith("telj"):
                processed_word = processed_word.removesuffix("telj")
            elif processed_word.endswith("teljic"):
                processed_word = processed_word.removesuffix("teljica")

            break

    return processed_word



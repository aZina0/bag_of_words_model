words = [
    "kuća", "kuće", "kuće", "kuća", "kući", "kućama", "kuću", "kuće", "kući", "kućama", "kućo", "kuće", "kućom", "kućama",
    "škola", "škole", "škole", "škola", "školi", "školama", "školu", "škole", "školi", "školama", "školo", "škole", "školom", "školama",
    "vrtić", "vrtići", "vrtića", "vrtića", "vrtiću", "vrtićima", "vrtić", "vrtiće", "vrtiću", "vrtićima", "vrtiće", "vrtići", "vrtićem", "vrtićima",
    "autobus", "autobusi", "autobusa", "autobusa", "autobusu", "autobusima", "autobus", "autobuse", "autobusu", "autobusima", "autobuse", "autobusi", "autobusom", "autobusima",
    "vlak", "vlakovi", "vlaka", "vlakova", "vlaku", "vlakovima", "vlak", "vlakove", "vlaku", "vlakovima", "vlaku", "vlakovi", "vlakom", "vlakovima",
    "sunce", "sunca", "sunca", "sunaca", "suncu", "suncima", "sunce", "sunca", "suncu", "suncima", "sunce", "sunca", "suncem", "suncima",
    "noć", "noći", "noći", "noći", "noći", "noćima", "noć", "noći", "noći", "noćima", "noći", "noći", "noći", "noću", "noćima",
    "banana", "banane", "banane", "banana", "banani", "bananama", "bananu", "banane", "banani", "bananama", "banano", "banane", "bananom", "bananama",
    "ove", "ovo",
    "učiteljica", "učiteljice", "učiteljice", "učiteljica", "učiteljici", "učiteljicama", "učiteljicu", "učiteljice", "učiteljici", "učiteljicama", "učiteljice", "učiteljice", "učiteljicom", "učiteljicama",
    "Najviše", "smo", "vremena", "posvetili", "Zakonu", "o", "plaćama", "Mislim", "da", "većina", "podržava", "smjer", "ali", "inzistiraju", "na", "donošenju", "podzakonskih", "akata", "do", "drugog", "čitanja", "A", "čuli", "smo", "da", "će", "se", "u", "tom", "smjeru", "i", "nastaviti", "već", "u", "prvim", "tjednima", "rujna", "kako", "bi", "se", "Zakon", "o", "plaćama", "službenika", "i", "namještenika", "donio", "do", "kraja", "ove", "godine", "ne", "bi", "li", "se", "već", "u", "veljači", "isplatila", "plaća", "za", "siječanj", "prema", "novim", "pravilima", "poručio", "je", "nakon", "sjednice", "Gospodarsko", "vijeća", "predsjednik", "tog", "tijela", "Ivan", "Mišetić",
]

suffixes = ["a", "e", "i", "ama", "u", "o", "om", "ima", "em", "ovi", "ova", "ovima", "ove", "ovima"]
suffixes.sort(key=len, reverse=True)

results = []

invalid_words = []
with open("invalid_words.txt", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if line != "" and line[0] != "/":
            invalid_words.append(line)

print(invalid_words)

for word in words:
    word = word.lower()
    success = False

    if word in invalid_words:
        continue

    for suffix in suffixes:
        if word.endswith(suffix) and word != suffix and len(word) > 2:
            processed_word = word.removesuffix(suffix)
            if processed_word not in results:
                results.append(processed_word)
            success = True
            break

    if not success:
        if word not in results:
            results.append(word)

results.sort()
print(results)

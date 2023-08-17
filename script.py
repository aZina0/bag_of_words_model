import requests
import stemming
import crodict_parser

vectors = {
    "politika": {},
    "gospodarstvo": {},
    "sport": {},
    "glazba": {},
    "filmovi_serije": {},
    "tehnologija": {},
}


invalid_words = []
with open("nebitne_rijeci.txt", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if line != "" and line[0] != "/":
            invalid_words.append(line)



def get_n_grams(html_text, n):
    f = open("temp/html.txt", "w", encoding="utf-8")
    f.write(html_text)
    f.close()

    while html_text.find("<!--") >= 0 and html_text.find("-->") >= 0:
        start_index = html_text.find("<!--")
        end_index = html_text.find("-->") + len("-->")
        html_text = html_text[0:start_index] + "\n" + html_text[end_index:-1]

    if html_text.find("<head>") >= 0:
        start_index = html_text.find("<head>")
        end_index = html_text.find("</head>") + len("</head>")
        html_text = html_text[0:start_index] + "\n" + html_text[end_index:-1]

    while html_text.find("<script") >= 0 and html_text.find("</script>") >= 0:
        start_index = html_text.find("<script")
        end_index = html_text.find("</script>") + len("</script>")
        html_text = html_text[0:start_index] + "\n" + html_text[end_index:-1]

    while html_text.find("<style") >= 0 and html_text.find("</style>") >= 0:
        start_index = html_text.find("<style")
        end_index = html_text.find("</style>") + len("</style>")
        html_text = html_text[0:start_index] + "\n" + html_text[end_index:-1]

    for tag in ["a", "span", "b", "i", "sup", "strong"]:
        while html_text.find("<" + tag) >= 0 and html_text.find("</" + tag + ">") >= 0:
            tag_open_start = html_text.find("<" + tag)
            tag_open_end = html_text.find(">", tag_open_start) + len(">")
            html_text = html_text[0:tag_open_start] + html_text[tag_open_end:-1]

            tag_close_start = html_text.find("</" + tag + ">")
            if tag_close_start >= 0:
                tag_close_end = tag_close_start + len("</" + tag + ">")
                html_text = html_text[0:tag_close_start] + " " + html_text[tag_close_end:-1]

    while html_text.find("<") >= 0 and html_text.find(">") >= 0:
        start_index = html_text.find("<")
        end_index = html_text.find(">") + len(">")
        html_text = html_text[0:start_index] + "\n" + html_text[end_index:-1]

    html_text = html_text.replace("&#8194;", " ")
    html_text = html_text.replace("&#8211;", "-")
    html_text = html_text.replace("&#8212;", "-")
    html_text = html_text.replace("&#8216;", '"')
    html_text = html_text.replace("&#8217;", '"')
    html_text = html_text.replace("&#8220;", '"')
    html_text = html_text.replace("&#8221;", '"')
    html_text = html_text.replace("&#91;", " ")
    html_text = html_text.replace("&#93;", "")
    html_text = html_text.replace("&nbsp;", " ")

    sentence_list = html_text.split("\n")
    sentence_index = 0
    while sentence_index < len(sentence_list):
        sentence_list[sentence_index] = sentence_list[sentence_index].strip()
        if sentence_list[sentence_index] == "":
            sentence_list.pop(sentence_index)
            continue

        sentence_index += 1

    f = open("temp/raw_sentences.txt", "w", encoding="utf-8")
    for sentence in sentence_list:
        f.write(sentence)
        f.write("\n")
    f.close()

    sentence_index = 0
    while sentence_index < len(sentence_list):
        for character in [".", ",", ":", "!", "?"]:
            split_result = sentence_list[sentence_index].split(character)
            sentence_list[sentence_index] = split_result[0]
            sentence_list[sentence_index] = sentence_list[sentence_index].strip()

            insert_index = 1
            for result in split_result[1:]:
                sentence_list.insert(sentence_index + insert_index, result)
                insert_index += 1

        # while sentence_list[sentence_index].find("(") >= 0 and sentence_list[sentence_index].find(")") >= 0:
        #     start_index = sentence_list[sentence_index].find("(")
        #     end_index = sentence_list[sentence_index].find(")") + len(")")
        #     sentence_list.insert(sentence_index + 1, sentence_list[start_index+1:end_index-1])
        #     sentence_list[sentence_index] = sentence_list[sentence_index][:start_index] + sentence_list[sentence_index][end_index:]

        sentence_index += 1

    f = open("temp/split_sentences.txt", "w", encoding="utf-8")
    for sentence in sentence_list:
        f.write(sentence)
        f.write("\n")
    f.close()

    # Pretvori sve u lowercase
    for sentence_index in range(len(sentence_list)):
        sentence_list[sentence_index] = sentence_list[sentence_index].lower()


    n_grams = []

    sentence_index = 0
    while sentence_index < len(sentence_list):
        sentence_list[sentence_index] = sentence_list[sentence_index].split()
        sentence_index += 1

    sentence_index = 0
    while sentence_index < len(sentence_list):
        word_index = 0
        while word_index + n <= len(sentence_list[sentence_index]):
            n_grams.append(sentence_list[sentence_index][word_index:word_index+n])
            word_index += 1

        sentence_index += 1

    return n_grams



def parse_n_grams(n_grams):
    n_gram_index = 0
    while n_gram_index < len(n_grams):
        valid = True

        # Izbaci sve n_torke koje sadrže riječi koje se ne sastoje od znakova abecede
        for word in n_grams[n_gram_index]:
            if not word.isalpha():
                valid = False
                break

        if valid:
            # Izbaci sve n_torke koje sadrže riječi koje se smatraju kao neznačajne (veznici, čestice...)
            for word in n_grams[n_gram_index]:
                if word in invalid_words:
                    valid = False
                    break

        # if valid:
        #     word_index = 0
        #     while word_index < len(n_grams[n_gram_index]):
        #         n_grams[n_gram_index][word_index] = stemming.process_word(n_grams[n_gram_index][word_index])
        #         word_index += 1

        if valid:
            word_index = 0
            while word_index < len(n_grams[n_gram_index]):
                result = crodict_parser.get_stem_word(n_grams[n_gram_index][word_index])
                if result != "NOT_FOUND":
                    n_grams[n_gram_index][word_index] = result
                word_index += 1

        if not valid:
            n_grams.pop(n_gram_index)
            continue
        n_gram_index += 1

    return n_grams




def get_sorted_dictionary(dictionary):
    return dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))


def generate_base_vectors():
    for category in vectors:

        links = []
        with open("poveznice/" + category + ".txt", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line != "" and line[0] != "/":
                    links.append(line)

        vectors[category] = get_vector_from_links(links)
        vectors[category] = get_sorted_dictionary(vectors[category])

        print("GENERATED " + category)



def get_vector_from_links(links):
    summed_vector = {}
    for link in links:
        try:
            url = requests.get(link)
        except:
            print("Pogreška - nije moguće dohvatiti web-stranicu.")
            continue

        vector = get_vector(url.text)

        for n_gram in vector:
            if n_gram not in summed_vector:
                summed_vector[n_gram] = vector[n_gram]
            else:
                summed_vector[n_gram] += vector[n_gram]

    return summed_vector


def get_vector(text):
    vector = {}
    n_grams = get_n_grams(text, 1)
    n_grams = parse_n_grams(n_grams)

    f = open("temp/n_grams.txt", "w", encoding="utf-8")
    for n_gram in n_grams:
        f.write(" ".join(n_gram))
        f.write("\n")
    f.close()

    for n_gram in n_grams:
        n_gram = " ".join(n_gram)
        if n_gram not in vector:
            vector[n_gram] = 1
        else:
            vector[n_gram] += 1

    return vector




def calculate_probabilities(test_vector):
    hits = {}
    for category in vectors:
        hits[category] = {"count": 0, "vector": {}}

    for n_gram in test_vector:
        for category in vectors:
            if n_gram in vectors[category]:
                hits[category]["count"] += min(test_vector[n_gram], vectors[category][n_gram])
                hits[category]["vector"][n_gram] = min(test_vector[n_gram], vectors[category][n_gram])

    # Zbroji ukupna preklapanja kategorije
    category_hits_sum = 0
    for category in hits:
        category_hits_sum += hits[category]["count"]

        # Sortiraj vektore unutar kategorije po broju preklapanja
        hits[category]["vector"] = get_sorted_dictionary(hits[category]["vector"])

    # Sortiraj kategorije po ukupnom broju preklapanja
    hits = dict(sorted(hits.items(), key=lambda item: item[1]["count"], reverse=True))

    f = open("result.txt", "w", encoding="utf-8")
    for category in hits:
        if category_hits_sum > 0:
            category_percentage = hits[category]["count"] / category_hits_sum * 100
        else:
            category_percentage = 0
        print("{}: {:.2f}".format(category, category_percentage))
        f.write("{}: {:.2f} -> {}".format(category, category_percentage, hits[category]["count"]))
        f.write("\n")
        for key in hits[category]["vector"]:
            f.write(key + ": " + str(hits[category]["vector"][key]))
            f.write("\n")
        f.write("\n")
    f.close()


generate_base_vectors()

while True:
    print("Unesi 'tekst' za klasifikaciju ručno unesenog teksta.")
    print("Unesi 'poveznica' za klasifikaciju teksta preuzetog s web-stranice.")
    print("Unesi 'kraj' za zatvaranje programa.")

    user = input(": ").lower().strip()

    if user == "kraj":
        break

    elif user == "tekst":
        print("Unesi tekst. Ostavi prazno za povratak.")
        user_text = input(": ")

        if user_text == "":
            continue

        vector = get_vector(user_text)
        print(vector)
        calculate_probabilities(vector)

    elif user == "poveznica":
        print("Unesi poveznicu. Ostavi prazno za povratak.")
        user_link = input(": ")

        vector = get_vector_from_links([user_link])
        print(vector)
        calculate_probabilities(vector)


# tekst = "Marko je išao igrati nogomet. Išao je i David."

# vektor = {'marko': 1, 'je': 2, 'išao': 2, 'igrati': 1, 'nogomet': 1, 'i': 1, 'david': 1}

# tekst = tekst.replace(".", "")
# tekst = tekst.lower()
# tekst = tekst.split(" ")

# dictionary = {}
# for word in tekst:
#     if word not in dictionary:
#         dictionary[word] = 1
#     else:
#         dictionary[word] += 1

# print(dictionary)

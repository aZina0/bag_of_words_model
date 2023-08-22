import requests
import json
import stemming
import crodict_parser
import casopis_parsers

vectors = {
    "filmovi_serije": {},
    "glazba": {},
    "gospodarstvo": {},
    "politika": {},
    "sport": {},
    "tehnologija": {},
}


try:
    with open("parsed_links.txt", "r", encoding="utf-8") as parsed_links_file:
        parsed_links = json.load(parsed_links_file)
except:
    parsed_links = {}


try:
    with open("nebitne_rijeci.txt", "r", encoding="utf-8") as file:
        invalid_words = []
        for line in file:
            line = line.strip()
            if line != "" and line[0] != "/":
                invalid_words.append(line)
except:
    invalid_words = []




def get_simple_sentences(html_text):
    # f = open("temp/html.txt", "w", encoding="utf-8")
    # f.write(html_text)
    # f.close()

    while html_text.find("<!--") >= 0 and html_text.find("-->") >= 0:
        start_index = html_text.find("<!--")
        end_index = html_text.find("-->") + len("-->")
        html_text = html_text[:start_index] + "\n" + html_text[end_index:]

    if html_text.find("<head>") >= 0:
        start_index = html_text.find("<head>")
        end_index = html_text.find("</head>") + len("</head>")
        html_text = html_text[:start_index] + "\n" + html_text[end_index:]

    while html_text.find("<script") >= 0 and html_text.find("</script>") >= 0:
        start_index = html_text.find("<script")
        end_index = html_text.find("</script>") + len("</script>")
        html_text = html_text[:start_index] + "\n" + html_text[end_index:]

    while html_text.find("<style") >= 0 and html_text.find("</style>") >= 0:
        start_index = html_text.find("<style")
        end_index = html_text.find("</style>") + len("</style>")
        html_text = html_text[:start_index] + "\n" + html_text[end_index:]

    for tag in ["iframe", "strong", "span", "sup", "a", "b", "i"]:
        while html_text.find("<" + tag) >= 0 and html_text.find("</" + tag + ">") >= 0:
            tag_open_start = html_text.find("<" + tag)
            tag_open_end = html_text.find(">", tag_open_start) + len(">")
            # print("============")
            # print(tag)
            # print(html_text)
            # print(html_text[tag_open_start:tag_open_end])
            html_text = html_text[:tag_open_start] + html_text[tag_open_end:]

            tag_close_start = html_text.find("</" + tag + ">")
            if tag_close_start >= 0:
                tag_close_end = tag_close_start + len("</" + tag + ">")
                # print(html_text[tag_close_start:tag_close_end])
                html_text = html_text[:tag_close_start] + " " + html_text[tag_close_end:]

    while html_text.find("<") >= 0 and html_text.find(">") >= 0:
        start_index = html_text.find("<")
        end_index = html_text.find(">") + len(">")
        html_text = html_text[:start_index] + "\n" + html_text[end_index:]

    html_text = html_text.replace("&#8194;", " ")
    html_text = html_text.replace("&#8211;", "-")
    html_text = html_text.replace("&#8212;", "-")
    html_text = html_text.replace("&#8216;", '"')
    html_text = html_text.replace("&#8217;", '"')
    html_text = html_text.replace("&#8220;", '"')
    html_text = html_text.replace("&#8221;", '"')
    html_text = html_text.replace("&#8221;", '"')
    html_text = html_text.replace("&#91;", " ")
    html_text = html_text.replace("&#93;", "")
    html_text = html_text.replace("&nbsp;", " ")
    html_text = html_text.replace("\u00a0", " ")
    html_text = html_text.replace("\u200b", "")
    html_text = html_text.replace("\u201c", "")
    html_text = html_text.replace("\u201d", "")
    html_text = html_text.replace("\u201e", "")
    html_text = html_text.replace("\u00bb", "")
    html_text = html_text.replace("\u00ab", "")
    html_text = html_text.replace("\u2018", "")
    html_text = html_text.replace("\u2019", "")
    html_text = html_text.replace("\u2013", "-")
    html_text = html_text.replace("\u2026", ".")
    html_text = html_text.replace("\"", "")
    html_text = html_text.replace("'", "")

    sentence_list = html_text.split("\n")
    sentence_index = 0
    while sentence_index < len(sentence_list):
        sentence_list[sentence_index] = sentence_list[sentence_index].strip()
        if sentence_list[sentence_index] == "":
            sentence_list.pop(sentence_index)
            continue

        sentence_index += 1

    # f = open("temp/raw_sentences.txt", "w", encoding="utf-8")
    # for sentence in sentence_list:
    #     f.write(sentence)
    #     f.write("\n")
    # f.close()

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

    sentence_index = 0
    while sentence_index < len(sentence_list):
        if sentence_list[sentence_index].strip() == "":
            sentence_list.pop(sentence_index)
            continue

        sentence_index += 1

    return sentence_list



def parse_n_grams(n_grams, base_vector = False):
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
                result = crodict_parser.get_stem_word(n_grams[n_gram_index][word_index], request=base_vector)
                if result != "NOT_FOUND":
                    n_grams[n_gram_index][word_index] = result
                word_index += 1

        if valid:
            # Izbaci sve n_torke koje sadrže riječi koje se smatraju kao neznačajne (veznici, čestice...)
            for word in n_grams[n_gram_index]:
                if word in invalid_words:
                    valid = False
                    break

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

        vectors[category] = get_vector_from_links(links, 1, base_vector=True)
        vectors[category] = get_sorted_dictionary(vectors[category])

        print("GENERATED " + category)



def get_vector_from_links(links, n, base_vector = False):
    summed_vector = {}
    for link in links:
        # Obradi tekst iz poveznica ili samo ugrabi ako je tekst vec obraden
        if link in parsed_links:
            simple_sentences = parsed_links[link][:]
        else:
            parser_failed = True
            if link.startswith("https://www.24sata.hr"):
                text = casopis_parsers.get_document_content_from_24sata(link)
                if text != "NOTHING":
                    parser_failed = False
            elif link.startswith("https://www.novilist.hr"):
                text = casopis_parsers.get_document_content_from_novilist(link)
                if text != "NOTHING":
                    parser_failed = False

            if parser_failed:
                try:
                    text = requests.get(link).text
                except:
                    print("Pogreška - nije moguće dohvatiti web-stranicu.")
                    continue

            

            simple_sentences = get_simple_sentences(text)
            parsed_links[link] = simple_sentences[:]
            # if link == "https://www.novilist.hr/mozaik/glazba/nakon-kino-blagajni-barbie-rusi-rekorde-i-na-glazbenim-top-ljestvicama/?meta_refresh=true":
            #     print(text)
            #     print(simple_sentences)
            with open("parsed_links.txt", "w", encoding="utf-8") as parsed_links_file:
                json.dump(parsed_links, parsed_links_file, indent=1)

        vector = get_vector_from_simple_sentences(simple_sentences, n, base_vector, link)

        for n_gram in vector:
            if n_gram not in summed_vector:
                summed_vector[n_gram] = vector[n_gram]
            else:
                summed_vector[n_gram] += vector[n_gram]

    return summed_vector


def get_vector_from_simple_sentences(simple_sentences, n, base_vector = False, link = None):
    # Razdvoji riječi u stringu u listu riječi
    sentence_index = 0
    while sentence_index < len(simple_sentences):
        simple_sentences[sentence_index] = simple_sentences[sentence_index].split()
        sentence_index += 1

    n_grams = []
    sentence_index = 0
    while sentence_index < len(simple_sentences):
        word_index = 0
        while word_index + n <= len(simple_sentences[sentence_index]):
            n_grams.append(simple_sentences[sentence_index][word_index:word_index+n])
            word_index += 1

        sentence_index += 1

    n_grams = parse_n_grams(n_grams, base_vector)

    # f = open("temp/n_grams.txt", "w", encoding="utf-8")
    # for n_gram in n_grams:
    #     f.write(" ".join(n_gram))
    #     f.write("\n")
    # f.close()

    vector = {}
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


# parsed = casopis_parsers.get_document_content_from_novilist("https://www.novilist.hr/mozaik/glazba/nakon-kino-blagajni-barbie-rusi-rekorde-i-na-glazbenim-top-ljestvicama/?meta_refresh=true")
# print(parsed)
# print(get_simple_sentences(parsed))


generate_base_vectors()
# print(vectors["politika"])

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

        simple_sentences = get_simple_sentences(user_text)
        vector = get_vector_from_simple_sentences(simple_sentences, 1)
        print(vector)
        calculate_probabilities(vector)

    elif user == "poveznica":
        print("Unesi poveznicu. Ostavi prazno za povratak.")
        user_link = input(": ")

        vector = get_vector_from_links([user_link], 1)
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

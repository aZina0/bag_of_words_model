import requests
import json
import stemming
import crodict_parser
import content_extractor
import math
import win32clipboard
import time

settings = {
    "N": 1,
    "remove_invalid_words": False,
    "prefix_suffix_removal": False,
    "crodict_database": False,
    "calculation_type": "count",
}


category_vectors = {
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
            html_text = html_text[:tag_open_start] + html_text[tag_open_end:]

            tag_close_start = html_text.find("</" + tag + ">")
            if tag_close_start >= 0:
                tag_close_end = tag_close_start + len("</" + tag + ">")
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
        n_gram = n_grams[n_gram_index]

        valid = True

        # Preskoči sve n_torke koje sadrže riječi koje se ne sastoje od znakova abecede
        for word in n_gram:
            if not word.isalpha():
                valid = False
                break

        if valid:
            if settings["remove_invalid_words"]:
                # Preskoči n-torku ako sadrži riječ koja
                # se smatra kao nebitna (veznici, čestice...)
                for word in n_gram:
                    if word in invalid_words:
                        valid = False
                        break

        if valid:
            if settings["prefix_suffix_removal"]:
                word_index = 0
                while word_index < len(n_grams[n_gram_index]):
                    n_grams[n_gram_index][word_index] = stemming.process_word(n_grams[n_gram_index][word_index])
                    word_index += 1

        if valid:
            if settings["crodict_database"]:
                word_index = 0
                while word_index < len(n_grams[n_gram_index]):
                    result = crodict_parser.get_stem_word(n_grams[n_gram_index][word_index], request=base_vector)
                    if result != "NOT_FOUND":
                        n_grams[n_gram_index][word_index] = result
                    word_index += 1

        if valid:
            if settings["remove_invalid_words"]:
                # Izbaci sve n-torke koje sadrže riječi koje
                # se smatraju kao nebitne (veznici, čestice...)
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


def generate_base_category_vectors():
    for category in category_vectors:

        links = []
        with open("poveznice/" + category + ".txt", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line != "" and line[0] != "/":
                    links.append(line)

        category_vectors[category]["separate"], category_vectors[category]["summed"] = get_vectors_from_links(links, base_vector=True)
        category_vectors[category]["summed"] = get_sorted_dictionary(category_vectors[category]["summed"])

        # print("GENERATED " + category)



def get_vectors_from_links(links, base_vector = False):
    vectors = {}
    summed_vector = {}
    for link in links:
        # Obradi tekst iz poveznica ili samo ugrabi ako je tekst vec obraden
        if link in parsed_links:
            simple_sentences = parsed_links[link][:]
        else:
            text = content_extractor.get_document_content(link)
            if text == "NOTHING":
                try:
                    text = requests.get(link).text
                except:
                    print("Pogreška - nije moguće dohvatiti web-stranicu.")
                    continue

            simple_sentences = get_simple_sentences(text)

            if base_vector:
                parsed_links[link] = simple_sentences[:]
                with open("parsed_links.txt", "w", encoding="utf-8") as parsed_links_file:
                    json.dump(parsed_links, parsed_links_file, indent=1)

        vectors[link] = get_vector_from_simple_sentences(simple_sentences, base_vector, link)
        vectors[link] = get_sorted_dictionary(vectors[link])

        for n_gram in vectors[link]:
            if n_gram not in summed_vector:
                summed_vector[n_gram] = vectors[link][n_gram]
            else:
                summed_vector[n_gram] += vectors[link][n_gram]

    if base_vector:
        return vectors, summed_vector
    else:
        return summed_vector

    # tf = {}
    # for link in links:
    #     tf[link] = {}
    #     total_count_of_n_grams = 0
    #     for n_gram in category_vectors[link]:
    #         total_count_of_n_grams += category_vectors[link][n_gram]

    #     for n_gram in category_vectors[link]:
    #         tf[link][n_gram] = category_vectors[link][n_gram] / total_count_of_n_grams

    #     tf[link] = get_sorted_dictionary(tf[link])

    # idf = {}
    # for n_gram in summed_vector:
    #     number_of_links_where_it_appears = 0

    #     for link in links:
    #         if n_gram in category_vectors[link]:
    #             number_of_links_where_it_appears += 1

    #     idf[n_gram] = 20 / number_of_links_where_it_appears

    # idf = get_sorted_dictionary(idf)

    # with open("temp/tf.txt", "w", encoding="utf-8") as file:
    #     json.dump(tf, file, indent=1)

    # with open("temp/idf.txt", "w", encoding="utf-8") as file:
    #     json.dump(idf, file, indent=1)

    # tfidf = {}
    # for link in links:
    #     tfidf[link] = {}

    #     for n_gram in category_vectors[link]:
    #         tfidf[link][n_gram] = tf[link][n_gram] * idf[n_gram]

    #     tfidf[link] = get_sorted_dictionary(tfidf[link])

    # with open("temp/tfidf.txt", "w", encoding="utf-8") as file:
    #     json.dump(tfidf, file, indent=1)

    # summ = {}
    # for n_gram in summed_vector:
    #     tfidfs = [0.0]

    #     for link in links:
    #         if n_gram in tfidf[link]:
    #             tfidfs.append(tfidf[link][n_gram])

    #     summ[n_gram] = max(tfidfs)

    # summ = get_sorted_dictionary(summ)

    # with open("temp/summ.txt", "w", encoding="utf-8") as file:
    #     json.dump(summ, file, indent=1)

    # return summed_vector


def get_vector_from_simple_sentences(simple_sentences, base_vector = False, link = None):
    # Razdvoji riječi u stringu u listu riječi
    sentence_index = 0
    while sentence_index < len(simple_sentences):
        simple_sentences[sentence_index] = simple_sentences[sentence_index].split()
        sentence_index += 1

    n_grams = []
    sentence_index = 0
    while sentence_index < len(simple_sentences):
        word_index = 0
        while word_index + settings["N"] <= len(simple_sentences[sentence_index]):
            n_grams.append(simple_sentences[sentence_index][word_index:word_index + settings["N"]])
            word_index += 1

        sentence_index += 1

    n_grams = parse_n_grams(n_grams, base_vector)

    vector = {}
    for n_gram in n_grams:
        n_gram = " ".join(n_gram)
        if n_gram not in vector:
            vector[n_gram] = 1
        else:
            vector[n_gram] += 1

    return vector



def get_probabilities_using_binary(test_vector, sort = True):
    hits = {}
    for category in category_vectors:
        hits[category] = {"count": 0, "n_grams": []}

    for n_gram in test_vector:
        for category in category_vectors:
            if n_gram in category_vectors[category]["summed"]:
                hits[category]["count"] += 1
                hits[category]["n_grams"].append(n_gram)

    # Zbroji ukupna preklapanja kategorije
    category_hits_sum = 0
    for category in hits:
        category_hits_sum += hits[category]["count"]

    # Sortiraj kategorije po ukupnom broju preklapanja
    if sort:
        hits = dict(sorted(hits.items(), key=lambda item: item[1]["count"], reverse=True))

    result = {}
    with open("rezultat.txt", "w", encoding="utf-8") as file:
        for category in hits:
            if category_hits_sum > 0:
                category_percentage = hits[category]["count"] / category_hits_sum * 100
            else:
                category_percentage = 0

            result[category] = category_percentage

            file.write("{}: {:.2f}% -> {}/{}\n".format(category.upper(), category_percentage, hits[category]["count"], category_hits_sum))
            file.write("")
            for n_gram in hits[category]["n_grams"]:
                file.write("'" + n_gram + "'")
                file.write("\n")
            file.write("\n")

    return result


def get_probabilities_using_count(test_vector, sort = True):
    hits = {}
    for category in category_vectors:
        hits[category] = {"count": 0, "vector": {}}

    for n_gram in test_vector:
        for category in category_vectors:
            if n_gram in category_vectors[category]["summed"]:
                hits[category]["count"] += min(test_vector[n_gram], category_vectors[category]["summed"][n_gram])
                hits[category]["vector"][n_gram] = min(test_vector[n_gram], category_vectors[category]["summed"][n_gram])

    # Zbroji ukupna preklapanja kategorije
    category_hits_sum = 0
    for category in hits:
        category_hits_sum += hits[category]["count"]

        # Sortiraj vektore unutar kategorije po broju preklapanja
        hits[category]["vector"] = get_sorted_dictionary(hits[category]["vector"])

    # Sortiraj kategorije po ukupnom broju preklapanja
    if sort:
        hits = dict(sorted(hits.items(), key=lambda item: item[1]["count"], reverse=True))

    result = {}
    with open("rezultat.txt", "w", encoding="utf-8") as file:
        for category in hits:
            if category_hits_sum > 0:
                category_percentage = hits[category]["count"] / category_hits_sum * 100
            else:
                category_percentage = 0

            result[category] = category_percentage

            file.write("{}: {:.2f}% -> {}/{}\n".format(category.upper(), category_percentage, hits[category]["count"], category_hits_sum))
            for n_gram in hits[category]["vector"]:
                file.write("'" + n_gram + "': " + str(hits[category]["vector"][n_gram]))
                file.write("\n")
            file.write("\n")

    return result


def get_probabilities_using_tfidf(test_vector, sort = True):
    tf = {}
    for category in category_vectors:
        tf[category] = {}
        count_of_n_grams_in_category = 0
        for n_gram in category_vectors[category]["summed"]:
            count_of_n_grams_in_category += category_vectors[category]["summed"][n_gram]

        for n_gram in category_vectors[category]["summed"]:
            if count_of_n_grams_in_category == 0:
                tf[category][n_gram] = 0
            else:
                tf[category][n_gram] = math.log10(category_vectors[category]["summed"][n_gram] / count_of_n_grams_in_category + 1)

        tf[category] = get_sorted_dictionary(tf[category])

    idf = {}
    for category in category_vectors:
        idf[category] = {}
        for n_gram in category_vectors[category]["summed"]:
            link_count = 0
            link_count_where_n_gram_appears = 0

            for link in category_vectors[category]["separate"]:
                link_count += 1
                if n_gram in category_vectors[category]["separate"][link]:
                    link_count_where_n_gram_appears += 1

            if link_count_where_n_gram_appears == 0:
                idf[category][n_gram] = 0
            else:
                idf[category][n_gram] = math.log10(link_count / link_count_where_n_gram_appears)

        idf[category] = get_sorted_dictionary(idf[category])


    tfidf = {}
    for category in category_vectors:
        tfidf[category] = {}

        for n_gram in category_vectors[category]["summed"]:
            tfidf[category][n_gram] = tf[category][n_gram] * idf[category][n_gram]

        tfidf[category] = get_sorted_dictionary(tfidf[category])


    with open("temp/tf.txt", "w", encoding="utf-8") as file:
        json.dump(tf, file, indent=4)

    with open("temp/idf.txt", "w", encoding="utf-8") as file:
        json.dump(idf, file, indent=4)

    with open("temp/tfidf.txt", "w", encoding="utf-8") as file:
        json.dump(tfidf, file, indent=4)


    test_tf = {}
    n_gram_count = 0
    for n_gram in test_vector:
        n_gram_count += 1

    for n_gram in test_vector:
        if n_gram == 0:
            test_tf[n_gram] = 0
        else:
            test_tf[n_gram] = math.log10(test_vector[n_gram] / n_gram_count + 1)


    hits = {}
    for category in category_vectors:
        hits[category] = {"count": 0, "vector": {}}

    for n_gram in test_vector:
        for category in category_vectors:
            if n_gram in category_vectors[category]["summed"]:
                hits[category]["vector"][n_gram] = tfidf[category][n_gram] * test_tf[n_gram]
                hits[category]["count"] += hits[category]["vector"][n_gram]

    # Zbroji ukupna preklapanja kategorije
    category_hits_sum = 0
    for category in hits:
        category_hits_sum += hits[category]["count"]

        # Sortiraj vektore unutar kategorije po broju preklapanja
        hits[category]["vector"] = get_sorted_dictionary(hits[category]["vector"])

    # Sortiraj kategorije po ukupnom broju preklapanja
    if sort:
        hits = dict(sorted(hits.items(), key=lambda item: item[1]["count"], reverse=True))

    result = {}
    with open("rezultat.txt", "w", encoding="utf-8") as file:
        for category in hits:
            if category_hits_sum > 0:
                category_percentage = hits[category]["count"] / category_hits_sum * 100
            else:
                category_percentage = 0

            result[category] = category_percentage

            file.write("{}: {:.2f}% -> {}/{}\n".format(category, category_percentage, hits[category]["count"], category_hits_sum))
            file.write("-------------------------\n")
            for n_gram in hits[category]["vector"]:
                file.write(n_gram + ": " + str(hits[category]["vector"][n_gram]))
                file.write("\n")
            file.write("\n")

    return result



settings = {
    "N": 1,
    "remove_invalid_words": False,
    "prefix_suffix_removal": False,
    "crodict_database": True,
    "calculation_type": "count",
}
generate_base_category_vectors()

test_links = {
    "Lud, zbunjen, normalan": "https://hr.wikipedia.org/wiki/Lud,_zbunjen,_normalan",
    "Oliver Dragojević": "https://hr.wikipedia.org/wiki/Oliver_Dragojevi%C4%87",
    "Inflacija": "https://hr.wikipedia.org/wiki/Inflacija",
    "Zoran Milanović": "https://hr.wikipedia.org/wiki/Zoran_Milanovi%C4%87",
    "Luka Modrić": "https://hr.wikipedia.org/wiki/Luka_Modri%C4%87",
    "Računalo": "https://hr.wikipedia.org/wiki/Ra%C4%8Dunalo",
}

clipboard = ""
for title in test_links:
    vector = get_vectors_from_links([test_links[title]])
    print(title)
    # print(vector)
    # print()
    result = get_probabilities_using_tfidf(vector, False)

    for category in result:
        clipboard += "{:.2f}%\t".format(result[category])
    clipboard += "\n"

win32clipboard.OpenClipboard()
win32clipboard.EmptyClipboard()
win32clipboard.SetClipboardText(clipboard.replace(".", ","), win32clipboard.CF_UNICODETEXT)
win32clipboard.CloseClipboard()
print("Copied to clipboard")


# while True:
#     print("Unesi 'tekst' za klasifikaciju ručno unesenog teksta.")
#     print("Unesi 'poveznica' za klasifikaciju teksta preuzetog s web-stranice.")
#     print("Unesi 'metoda' za izmjenu metoda klasificiranja.")
#     print("Unesi 'kraj' za zatvaranje programa.")

#     user = input(": ").lower().strip()
#     print()

#     if user == "kraj":
#         break

#     elif user == "tekst":
#         print("Unesi tekst. Ostavi prazno za povratak.")
#         user_text = input(": ")

#         if user_text == "":
#             continue

#         simple_sentences = get_simple_sentences(user_text)
#         vector = get_vector_from_simple_sentences(simple_sentences, settings["N"])

#         result = {}
#         if settings["calculation_type"] == "binary":
#             result = get_probabilities_using_binary(vector)
#         elif settings["calculation_type"] == "count":
#             result = get_probabilities_using_count(vector)
#         elif settings["calculation_type"] == "tf-idf":
#             result = get_probabilities_using_tfidf(vector)

#         print()
#         print("Rezultati klasifikacije:")
#         for category in result:
#             print("{}: {:.2f}%".format(category, result[category]))
#         print()

#     elif user == "poveznica":
#         print("Unesi poveznicu. Ostavi prazno za povratak.")
#         user_link = input(": ")
#         start = time.time()
#         vector = get_vector_from_links([user_link], settings["N"])

#         result = {}
#         if settings["calculation_type"] == "binary":
#             result = get_probabilities_using_binary(vector)
#         elif settings["calculation_type"] == "count":
#             result = get_probabilities_using_count(vector)
#         elif settings["calculation_type"] == "tf-idf":
#             result = get_probabilities_using_tfidf(vector)

#         print()
#         print("Rezultati klasifikacije:")
#         for category in result:
#             print("{}: {:.2f}%".format(category, result[category]))
#         print(time.time() - start)
#         print()


#     elif user == "metoda":
#         print("Unesi 'n-torka N' za izmjenu koliko se riječi povezuje u skup, gdje je N broj riječi.")
#         print("Unesi 'ukloni-nebitne' za automatsko uklanjanje nebitnih riječi.")
#         print("Unesi 'dopusti-nebitne' za dopuštanje nebitnih riječi.")
#         print("Unesi 'omoguci-prefiks-sufiks' za automatsko uklanjanje definiranih prefiksa/sufiksa.")
#         print("Unesi 'onemoguci-prefiks-sufiks' za onemogaćavanje automatskog uklanjanja definiranih prefiksa/sufiksa.")
#         print("Unesi 'omoguci-baza-podataka' za automatsko povezivanje n-torki prema njihovim poznatim oblicima.")
#         print("Unesi 'onemoguci-baza-podataka' za onemogaćavanje automatskog povezivanja n-torki prema njihovim poznatim oblicima.")
#         print("Unesi 'bodovanje METODA' za izmjenu metode bodovanja n-torki. METODA može biti 'binarno', 'ponavljanje' ili 'tf-idf'.")
#         print("Ostavi prazno za povratak.")

#         user_method = input(": ")

#         user_method_split = user_method.split(" ")
#         if user_method_split[0] == "n-torka" and user_method_split[1].isdigit():
#             if int(user_method_split[1]) in [1, 2, 3, 4]:
#                 settings["N"] = int(user_method_split[1])

#         elif user_method_split[0] == "bodovanje":
#             if user_method_split[1] == "binarno":
#                 settings["calculation_type"] = "binary"
#             elif user_method_split[1] == "ponavljanje":
#                 settings["calculation_type"] = "count"
#             elif user_method_split[1] == "tf-idf":
#                 settings["calculation_type"] = "tf-idf"

#         elif user_method == "ukloni-nebitne":
#             settings["remove_invalid_words"] = True
#         elif user_method == "dopusti-nebitne":
#             settings["remove_invalid_words"] = False

#         elif user_method == "omoguci-prefiks-sufiks":
#             settings["prefix_suffix_removal"] = True
#         elif user_method == "onemoguci-prefiks-sufiks":
#             settings["prefix_suffix_removal"] = False

#         elif user_method == "omoguci-baza-podataka":
#             settings["crodict_database"] = True
#         elif user_method == "onemoguci-baza-podataka":
#             settings["crodict_database"] = False

#         else:
#             if user_method != "":
#                 print("Neispravan unos.")
#             elif user_method == "":
#                 pass

#         category_vectors.clear()
#         generate_base_category_vectors()





# tekst = "Marko je išao igrati nogomet. Išao je i David."

# vektor = {'marko': 1, 'je': 2, 'išao': 2, 'igrati': 1, 'nogomet': 1, 'i': 1, 'david': 1}


# settings["crodict_database"] = True
# generate_base_category_vectors()


# tekst = "vrabac vrapci ronilac ronioca orahu orasi zadatkom zadaci"
# vektor = get_vector_from_simple_sentences([tekst])

# print(vektor)

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




# sport idf:        i: 0.1, nogomet: 1,     odbojka: 1.8,   kosarka: 1.2

# sport1 tf:        i: 10,  nogomet: 5,     odbojka: 0,     kosarka: 0
# sport2 tf:        i: 10,  nogomet: 0,     odbojka: 3,     kosarka: 0
# sport3 tf:        i: 10,  nogomet: 0,     odbojka: 0,     kosarka: 1

# sport1 tfidf:     i: 1,   nogomet: 5,     odbojka: 0,     kosarka: 0
# sport2 tfidf:     i: 1,   nogomet: 0,     odbojka: 5.4,   kosarka: 0
# sport3 tfidf:     i: 1,   nogomet: 0,     odbojka: 0,     kosarka: 1.2


# politika idf:     i: 0.1, nogomet: 2,     odbojka: -,     kosarka: -

# politika tf:      i: 10,  nogomet: 1,     odbojka: 0,     kosarka: 0
# politika tf:      i: 10,  nogomet: 0,     odbojka: 0,     kosarka: 0
# politika tf:      i: 10,  nogomet: 0,     odbojka: 0,     kosarka: 0

# politika tfidf:   i: 1,   nogomet: 2,     odbojka: 0,     kosarka: 0
# politika tfidf:   i: 1,   nogomet: 0,     odbojka: 0,     kosarka: 0
# politika tfidf:   i: 1,   nogomet: 0,     odbojka: 0,     kosarka: 0





# luka modrić tf:   i:50,   nogomet: 5,     odbojka: 0.5,   kosarka: 0

# sport             i:50,   nogomet: 25,    odbojka: 2.7,   kosarka: 0
# politika          i:50,   nogomet: 10,    odbojka: 0,     kosarka: 0


# luka modrić tf:   i:50,   nogomet: 5,     odbojka: 0.5,   kosarka: 0

# sport             i:5,   nogomet: 5,    odbojka: 2.7,   kosarka: 0
# politika          i:5,   nogomet: 10,    odbojka: 0,     kosarka: 0

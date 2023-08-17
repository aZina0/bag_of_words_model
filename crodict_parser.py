import requests
import json


absent_words = []
with open("crodict/nepronadene_rijeci.txt", "r", encoding="utf-8") as absent_words_file:
    for line in absent_words_file:
        absent_words.append(line.strip())


with open("crodict/rjecnik.txt", "r", encoding="utf-8") as dictionary_file:
    word_dictionary = json.load(dictionary_file)


def get_stem_word(word):
    if word in word_dictionary:
        return word_dictionary[word]

    if word in absent_words:
        return "NOT_FOUND"

    for word_type in ["imenice", "glagoli"]:
        try:
            url = requests.get("https://www.crodict.hr/" + word_type + "/hrvatski/" + word)
            print(word, "REQUESTED")
            # with open("parsed.txt", "w", encoding="utf-8") as result_file:
            #     result_file.write(url.text)
        except:
            print("COULDN'T REQUEST HTML")
            continue

        if url.text.find("Der gesuchte Begriff konnte nicht gefunden werden") != -1:
            continue


        for vrsta_rijeci_tekst in ["Deklinacija od", "Konjugacija od"]:
            if url.text.find(vrsta_rijeci_tekst) > -1:
                vrsta_rijeci_end = url.text.find(vrsta_rijeci_tekst) + len(vrsta_rijeci_tekst)
                if url.text.find("<em>", vrsta_rijeci_end) > -1 and url.text.find("</em>", vrsta_rijeci_end) > -1:
                    em_start = url.text.find("<em>", vrsta_rijeci_end)
                    em_end = url.text.find("</em>", vrsta_rijeci_end)
                    base_form = url.text[em_start + len("<em>") : em_end].lower()

                other_forms = []
                other_forms.append(base_form)
                tag_start = url.text.find("<td>")
                tag_end = url.text.find("</td>", tag_start)

                while tag_start > -1 and tag_end > -1:
                    forms = url.text[tag_start + len("<td>") : tag_end].strip().split("/")
                    for form in forms:
                        form = form.strip()
                        if form == "-":
                            continue

                        verb = form.split(" ")
                        if len(verb) > 1:
                            form = verb[1]

                        if form not in other_forms:
                            other_forms.append(form.lower())

                    tag_start = url.text.find("<td>", tag_start + 1)
                    tag_end = url.text.find("</td>", tag_start)

                if word not in other_forms:
                    break

                for form in other_forms:
                    word_dictionary[form] = base_form

                with open("crodict/rjecnik.txt", "w", encoding="utf-8") as dictionary_file:
                    json.dump(word_dictionary, dictionary_file, indent=4)
                return base_form

    with open("crodict/nepronadene_rijeci.txt", "a", encoding="utf-8") as absent_words_file:
        absent_words_file.write(word + "\n")
        absent_words.append(word)
    return "NOT_FOUND"
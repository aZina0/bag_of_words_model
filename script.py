import requests


def get_sentence_list(html_text):
    f = open("html.txt", "w", encoding="utf-8")
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

    for tag in ["a", "span", "b", "i", "sup", "strong"]:
        while html_text.find("<" + tag) >= 0:
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

    f = open("raw_sentences.txt", "w", encoding="utf-8")
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

    f = open("split_sentences.txt", "w", encoding="utf-8")
    for sentence in sentence_list:
        f.write(sentence)
        f.write("\n")
    f.close()

    sentence_index = 0
    while sentence_index < len(sentence_list):
        sentence_list[sentence_index] = sentence_list[sentence_index].split()
        sentence_index += 1

    # Postavi sva slova svih riječi u "lowercase"
    for sentence_index in range(len(sentence_list)):
        for word_index in range(len(sentence_list[sentence_index])):
            sentence_list[sentence_index][word_index] = sentence_list[sentence_index][word_index].lower()

    # n-grami
    NUMBER = 3
    n_gram_list = []
    sentence_index = 0
    while sentence_index < len(sentence_list):
        word_index = 0
        while word_index + NUMBER <= len(sentence_list[sentence_index]):
            n_gram_list.append(sentence_list[sentence_index][word_index:word_index+NUMBER])
            word_index += 1

        sentence_index += 1

    # Izbaci sve n_grame koji sadrže riječi koje se ne sastoje od znakova abecede
    n_gram_index = 0
    while n_gram_index < len(n_gram_list):
        valid = True
        for word in n_gram_list[n_gram_index]:
            if not word.isalpha():
                valid = False
                break

        if not valid:
            n_gram_list.pop(n_gram_index)
            continue
        n_gram_index += 1

    f = open("n_grams.txt", "w", encoding="utf-8")
    for n_gram in n_gram_list:
        f.write(" ".join(n_gram))
        f.write("\n")
    f.close()

    return sentence_list


def parse_word_list(word_list):
    index = 0
    while index < len(word_list):
        for character in [".", ",", "?", "!", ":", ";", "(", ")", '"', "-", "«", "»"]:
            split_result = word_list[index].split(character)
            if len(split_result) > 1:
                word_list[index] = split_result[0]
                for word in split_result[1:]:
                    word_list.append(word)

        if not word_list[index].isalpha():
            if word_list[index] != "": print(word_list[index])
            del word_list[index]
            continue

        word_list[index] = word_list[index].lower()

        if word_list[index] in ["i", "pa", "te", "ni", "niti", "a", "ali", "nego", "već", "no", "na", "o", "po", "pri", "prema", "u", "je", "ostalo", "se", "za", "su", "s", "od", "da", "iz", "sa", "to", "ili", "koji", "kao", "što", "nakon", "do"]:
            # if word_list[index] != "": print(word_list[index])
            del word_list[index]
            continue

        index += 1


def get_sorted_dictionary(dictionary):
    return dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))


def get_vector_from_links(links):
    vector = {}
    for link in links:
        try:
            url = requests.get(link)
        except:
            continue

        html_text = url.text
        sentence_list = get_sentence_list(html_text)
        # parse_word_list(word_list)

        # for word in word_list:
        #     if word not in vector:
        #         vector[word] = 1
        #     else:
        #         vector[word] += 1

    # vector = get_sorted_dictionary(vector)
    # return vector


def calculate_probabilities(sport_vector, kultura_vector, lifestyle_vector, test_vector):
    hits = {
        "sport": {"count": 0, "vector": {}},
        "kultura": {"count": 0, "vector": {}},
        "lifestyle": {"count": 0, "vector": {}},
    }

    for key in test_vector:
        if key in sport_vector:
            hits["sport"]["count"] += min(test_vector[key], sport_vector[key])
            hits["sport"]["vector"][key] = min(test_vector[key], sport_vector[key])
        if key in kultura_vector:
            hits["kultura"]["count"] += min(test_vector[key], kultura_vector[key])
            hits["kultura"]["vector"][key] = min(test_vector[key], kultura_vector[key])
        if key in lifestyle_vector:
            hits["lifestyle"]["count"] += min(test_vector[key], lifestyle_vector[key])
            hits["lifestyle"]["vector"][key] = min(test_vector[key], lifestyle_vector[key])

    summ = hits["sport"]["count"] + hits["kultura"]["count"] + hits["lifestyle"]["count"]

    hits = dict(sorted(hits.items(), key=lambda item: item[1]["count"], reverse=True))

    f = open("result.txt", "w", encoding="utf-8")
    for category in hits:
        hits[category]["vector"] = dict(sorted(hits[category]["vector"].items(), key=lambda item: item[1], reverse=True))
        f.write(category + ": " + str(hits[category]["count"] / summ * 100) + " -> " + str(hits[category]["count"]))
        f.write("\n")
        for key in hits[category]["vector"]:
            f.write(key + ": " + str(hits[category]["vector"][key]))
            f.write("\n")
        f.write("\n")
    f.close()

sport_links = [
    "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/osijek/za-osijekov-potop-je-najzasluzniji-neocekivani-junak-odradio-je-sve-zaustavio-miereza-i-zabio-kad-je-trebalo-15335467",
    # "https://sportske.jutarnji.hr/sn/nogomet/nogomet-mix/video-bomba-hrvata-apsolutni-je-hit-bivsi-vatreni-slabijom-nogom-postigao-jedan-od-najljepsih-golova-u-karijeri-15335460",
    # "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/hajduk/video-dominantni-hajduk-napunio-mrezu-osijeka-u-derbiju-bijelima-ovako-nesto-nije-uspjelo-sedam-godina-15335421",
    # "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/istra1961/uzivo-video-ludnica-na-drosini-sijevaju-udarci-pred-vratima-istre-sebicnost-napadaca-drzi-goricu-na-zivotu-15335459",
    # "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/osijek/nakon-sto-je-hajduk-potopio-osijek-unatoc-pljusku-navijaci-nisu-odlazili-poruka-igracima-bila-je-jasna-15335478",
    # "https://sportske.jutarnji.hr/sn/nogomet/serie-a/video-spezia-sokirala-milan-za-sestu-pobjedu-sezone-u-borbi-za-opstanak-salernitana-iznenadila-atalantu-15335476",
    # "https://sportske.jutarnji.hr/sn/nogomet/hnl/druga-hnl/rudes-pregazio-dubravu-i-sa-stilom-potvrdio-povratak-medu-hrvatsku-elitu-pokazali-smo-karakter-15335472",
    # "https://sportske.jutarnji.hr/sn/tenis/atp-wta-turniri/smjena-na-vrhu-atp-ljestvice-alcaraz-nastavio-sjajnu-pobjednicku-seriju-i-svrgnuo-novaka-dokovica-15335475",
    # "https://sportske.jutarnji.hr/sn/nogomet/primera/video-vatreni-as-zabio-svoj-peti-ovosezonski-pogodak-zatresao-mrezu-u-maniri-hladnokrvnog-strijelca-15335443",
    # "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/osijek/tomas-imali-smo-kontrolu-do-gola-resetirat-cemo-se-leko-kada-lako-dobijes-osijek-sve-izgleda-ljepse-15335470",
]

kultura_links = [
    "https://www.jutarnji.hr/kultura/film-i-televizija/majcina-prerana-smrt-od-raka-kao-trauma-jedne-knjizevnice-u-novoj-seriji-u-produkciji-reese-witherspoon-15335425",
    # "https://www.jutarnji.hr/promo/spektakularne-queereeoke-uskoro-u-zagrebu-15333611?utm_source=upscore_box",
    # "https://www.jutarnji.hr/promo/jeste-li-sreli-prolaznike-zagreba-u-joga-pozama-ovih-dana-znate-li-o-kakvom-je-izazovu-rijec-15333504?utm_source=upscore_box",
    # "https://www.jutarnji.hr/kultura/art/pogledajte-atmosferu-na-jabukovcu-gdje-ove-subote-mladi-umjetnici-prodaju-svoja-djela-15335413",
    # "https://www.jutarnji.hr/kultura/glazba/donny-mccaslin-u-zagrebu-vec-od-prve-skladbe-bilo-je-jasno-da-je-mocan-i-povremeno-furiozan-saksofonist-15335324",
    # "https://www.jutarnji.hr/kultura/art/u-mesnickoj-je-sinoc-bio-usporen-promet-necete-vjerovati-koji-je-razlog-15335265",
    # "https://www.jutarnji.hr/kultura/glazba/bili-smo-na-probi-uoci-finala-prlja-pjeva-poput-ptice-bend-zvuci-i-izgleda-mocno-a-kraj-je-posebno-upecatljiv-15335173",
    # "https://www.jutarnji.hr/kultura/film-i-televizija/sljedeci-tjedan-rezerviran-je-za-32-dane-hrvatskog-filma-donosimo-detalje-bogatog-rasporeda-15335132",
    # "https://www.jutarnji.hr/kultura/glazba/prihod-koncerta-ane-rucner-i-kolega-usmjeren-je-na-potporu-obrazovanju-mladih-bez-adekvatne-roditeljske-skrbi-15335110",
    # "https://www.jutarnji.hr/promo/ministarstvo-je-odvojilo-530-tisuca-eura-za-sufinanciranje-solarnih-uredaja-za-zastitu-zemlje-i-uroda-evo-kako-do-njih-15333981",
]

lifestyle_links = [
    # "https://www.jutarnji.hr/life/zdravlje/nas-trgovacki-lanac-zbog-bakterije-povukao-proizvod-kupac-ga-htio-vratiti-ali-je-dobio-kosaricu-15335405",
    "https://www.jutarnji.hr/promo/sveobuhvatna-rekonstrukcija-ekstremiteta-kod-ortopedskih-karcinoma-15332401?utm_source=upscore_box",
    # "https://www.jutarnji.hr/promo/okusaj-izdrzljivost-i-pomakni-svoje-granice-na-najvecoj-svjetskoj-utrci-s-preprekama-15333478?utm_source=upscore_box",
    # "https://www.jutarnji.hr/promo/jeste-li-sreli-prolaznike-zagreba-u-joga-pozama-ovih-dana-znate-li-o-kakvom-je-izazovu-rijec-15333504?utm_source=upscore_box",
    # "https://www.jutarnji.hr/life/zivotne-price/rekla-je-da-i-par-sekundi-poslije-postala-zrtva-pijane-vozacice-nisam-ucinila-nista-lose-hocu-doma-15335332",
    # "https://www.jutarnji.hr/domidizajn/nekretnine/prodaje-se-zgrada-na-zagrebackom-ribnjaku-za-3-5-milijuna-eura-15335136",
    # "https://www.jutarnji.hr/life/zivotne-price/finska-bruji-o-raspadu-braka-sanne-marin-za-sve-je-kriva-fatalna-indijka-procurile-i-fotke-15335349",
    # "https://www.jutarnji.hr/life/zdravlje/nije-prestajala-kasljati-doktor-joj-prepisao-antibiotik-nakon-par-mjeseci-shvatila-je-o-kakvoj-se-pogresci-radi-15335250",
    # "https://www.jutarnji.hr/life/tehnologija/nova-era-na-pomolu-musk-objavio-tko-dolazi-na-mjesto-glavnog-izvrsnog-direktora-twittera-15335222",
    # "https://www.jutarnji.hr/life/tehnologija/facebook-spijuni-oprez-drustvena-mreza-korisnicima-koje-promatrate-salje-zahtjeve-za-prijateljstvima-15335197",
]

# sport_vector = get_vector_from_links(sport_links)
# kultura_vector = get_vector_from_links(kultura_links)
lifestyle_vector = get_vector_from_links(lifestyle_links)

# print(sport_vector)

# test_vector = get_vector_from_links(["https://hr.wikipedia.org/wiki/Luka_Modri%C4%87"])

# calculate_probabilities(sport_vector, kultura_vector, lifestyle_vector, test_vector)
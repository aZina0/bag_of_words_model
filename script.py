import requests


def get_clean_word_list(html_text):

    while html_text.find("<!--") >= 0 and html_text.find("-->") >= 0:
        start_index = html_text.find("<!--")
        end_index = html_text.find("-->") + len("-->")
        html_text = html_text[0:start_index] + " " + html_text[end_index:-1]

    if html_text.find("<head>") >= 0:
        start_index = html_text.find("<head>")
        end_index = html_text.find("</head>") + len("</head>")
        html_text = html_text[0:start_index] + " " + html_text[end_index:-1]

    while html_text.find("<script") >= 0 and html_text.find("</script>") >= 0:
        start_index = html_text.find("<script")
        end_index = html_text.find("</script>") + len("</script>")
        html_text = html_text[0:start_index] + " " + html_text[end_index:-1]

    while html_text.find("<") >= 0 and html_text.find(">") >= 0:
        start_index = html_text.find("<")
        end_index = html_text.find(">") + len(">")
        html_text = html_text[0:start_index] + " " + html_text[end_index:-1]

    html_text = html_text.replace("&#8220", '"')
    html_text = html_text.replace("&#8221", '"')
    html_text = html_text.replace("&#8216", '"')
    html_text = html_text.replace("&#8217", '"')
    html_text = html_text.replace("&#8211", '-')
    html_text = html_text.split()

    return html_text


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
            # print(word_list[index])
            del word_list[index]
            continue

        word_list[index] = word_list[index].lower()
        index += 1


# def get_vector(word_list):
#     for word in word_list:
#         if word not in vector:
#             vector[word] = 0
#         else:
#             vector[word] += 1
#     return vector


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
        word_list = get_clean_word_list(html_text)
        parse_word_list(word_list)

        for word in word_list:
            if word not in vector:
                vector[word] = 0
            else:
                vector[word] += 1

    vector = get_sorted_dictionary(vector)
    return vector


def calculate_probabilities(sport_vector, kultura_vector, lifestyle_vector, test_vector):
    hits = {
        "sport": 0,
        "kultura": 0,
        "lifestyle": 0,
    }

    for key in test_vector:
        if key in sport_vector:
            hits["sport"] += min(test_vector[key], sport_vector[key])
        if key in kultura_vector:
            hits["kultura"] += min(test_vector[key], kultura_vector[key])
        if key in lifestyle_vector:
            hits["lifestyle"] += min(test_vector[key], lifestyle_vector[key])

    summ = hits["sport"] + hits["kultura"] + hits["lifestyle"]

    hits = get_sorted_dictionary(hits)
    for category in hits:
        print(category, hits[category] / summ * 100)

sport_links = [
    "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/osijek/za-osijekov-potop-je-najzasluzniji-neocekivani-junak-odradio-je-sve-zaustavio-miereza-i-zabio-kad-je-trebalo-15335467",
    "https://sportske.jutarnji.hr/sn/nogomet/nogomet-mix/video-bomba-hrvata-apsolutni-je-hit-bivsi-vatreni-slabijom-nogom-postigao-jedan-od-najljepsih-golova-u-karijeri-15335460",
    "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/hajduk/video-dominantni-hajduk-napunio-mrezu-osijeka-u-derbiju-bijelima-ovako-nesto-nije-uspjelo-sedam-godina-15335421",
    "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/istra1961/uzivo-video-ludnica-na-drosini-sijevaju-udarci-pred-vratima-istre-sebicnost-napadaca-drzi-goricu-na-zivotu-15335459",
    "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/osijek/nakon-sto-je-hajduk-potopio-osijek-unatoc-pljusku-navijaci-nisu-odlazili-poruka-igracima-bila-je-jasna-15335478",
    "https://sportske.jutarnji.hr/sn/nogomet/serie-a/video-spezia-sokirala-milan-za-sestu-pobjedu-sezone-u-borbi-za-opstanak-salernitana-iznenadila-atalantu-15335476",
    "https://sportske.jutarnji.hr/sn/nogomet/hnl/druga-hnl/rudes-pregazio-dubravu-i-sa-stilom-potvrdio-povratak-medu-hrvatsku-elitu-pokazali-smo-karakter-15335472",
    "https://sportske.jutarnji.hr/sn/tenis/atp-wta-turniri/smjena-na-vrhu-atp-ljestvice-alcaraz-nastavio-sjajnu-pobjednicku-seriju-i-svrgnuo-novaka-dokovica-15335475",
    "https://sportske.jutarnji.hr/sn/nogomet/primera/video-vatreni-as-zabio-svoj-peti-ovosezonski-pogodak-zatresao-mrezu-u-maniri-hladnokrvnog-strijelca-15335443",
    "https://sportske.jutarnji.hr/sn/nogomet/hnl/klubovi/osijek/tomas-imali-smo-kontrolu-do-gola-resetirat-cemo-se-leko-kada-lako-dobijes-osijek-sve-izgleda-ljepse-15335470",
]

kultura_links = [
    "https://www.jutarnji.hr/kultura/film-i-televizija/majcina-prerana-smrt-od-raka-kao-trauma-jedne-knjizevnice-u-novoj-seriji-u-produkciji-reese-witherspoon-15335425",
    "https://www.jutarnji.hr/promo/spektakularne-queereeoke-uskoro-u-zagrebu-15333611?utm_source=upscore_box",
    "https://www.jutarnji.hr/promo/jeste-li-sreli-prolaznike-zagreba-u-joga-pozama-ovih-dana-znate-li-o-kakvom-je-izazovu-rijec-15333504?utm_source=upscore_box",
    "https://www.jutarnji.hr/kultura/art/pogledajte-atmosferu-na-jabukovcu-gdje-ove-subote-mladi-umjetnici-prodaju-svoja-djela-15335413",
    "https://www.jutarnji.hr/kultura/glazba/donny-mccaslin-u-zagrebu-vec-od-prve-skladbe-bilo-je-jasno-da-je-mocan-i-povremeno-furiozan-saksofonist-15335324",
    "https://www.jutarnji.hr/kultura/art/u-mesnickoj-je-sinoc-bio-usporen-promet-necete-vjerovati-koji-je-razlog-15335265",
    "https://www.jutarnji.hr/kultura/glazba/bili-smo-na-probi-uoci-finala-prlja-pjeva-poput-ptice-bend-zvuci-i-izgleda-mocno-a-kraj-je-posebno-upecatljiv-15335173",
    "https://www.jutarnji.hr/kultura/film-i-televizija/sljedeci-tjedan-rezerviran-je-za-32-dane-hrvatskog-filma-donosimo-detalje-bogatog-rasporeda-15335132",
    "https://www.jutarnji.hr/kultura/glazba/prihod-koncerta-ane-rucner-i-kolega-usmjeren-je-na-potporu-obrazovanju-mladih-bez-adekvatne-roditeljske-skrbi-15335110",
    "https://www.jutarnji.hr/promo/ministarstvo-je-odvojilo-530-tisuca-eura-za-sufinanciranje-solarnih-uredaja-za-zastitu-zemlje-i-uroda-evo-kako-do-njih-15333981",
]

lifestyle_links = [
    "https://www.jutarnji.hr/life/zdravlje/nas-trgovacki-lanac-zbog-bakterije-povukao-proizvod-kupac-ga-htio-vratiti-ali-je-dobio-kosaricu-15335405",
    "https://www.jutarnji.hr/promo/sveobuhvatna-rekonstrukcija-ekstremiteta-kod-ortopedskih-karcinoma-15332401?utm_source=upscore_box",
    "https://www.jutarnji.hr/promo/okusaj-izdrzljivost-i-pomakni-svoje-granice-na-najvecoj-svjetskoj-utrci-s-preprekama-15333478?utm_source=upscore_box",
    "https://www.jutarnji.hr/promo/jeste-li-sreli-prolaznike-zagreba-u-joga-pozama-ovih-dana-znate-li-o-kakvom-je-izazovu-rijec-15333504?utm_source=upscore_box",
    "https://www.jutarnji.hr/life/zivotne-price/rekla-je-da-i-par-sekundi-poslije-postala-zrtva-pijane-vozacice-nisam-ucinila-nista-lose-hocu-doma-15335332",
    "https://www.jutarnji.hr/domidizajn/nekretnine/prodaje-se-zgrada-na-zagrebackom-ribnjaku-za-3-5-milijuna-eura-15335136",
    "https://www.jutarnji.hr/life/zivotne-price/finska-bruji-o-raspadu-braka-sanne-marin-za-sve-je-kriva-fatalna-indijka-procurile-i-fotke-15335349",
    "https://www.jutarnji.hr/life/zdravlje/nije-prestajala-kasljati-doktor-joj-prepisao-antibiotik-nakon-par-mjeseci-shvatila-je-o-kakvoj-se-pogresci-radi-15335250",
    "https://www.jutarnji.hr/life/tehnologija/nova-era-na-pomolu-musk-objavio-tko-dolazi-na-mjesto-glavnog-izvrsnog-direktora-twittera-15335222",
    "https://www.jutarnji.hr/life/tehnologija/facebook-spijuni-oprez-drustvena-mreza-korisnicima-koje-promatrate-salje-zahtjeve-za-prijateljstvima-15335197",
]

sport_vector = get_vector_from_links(sport_links)
kultura_vector = get_vector_from_links(kultura_links)
lifestyle_vector = get_vector_from_links(lifestyle_links)

test_vector = get_vector_from_links(["https://hr.wikipedia.org/wiki/Umjetnost"])

calculate_probabilities(sport_vector, kultura_vector, lifestyle_vector, test_vector)

# url = requests.get("https://www.novilist.hr/novosti/hrvatska/suci-su-u-bijelom-strajku-a-hrvatska-pri-vrhu-eu-a-po-broju-nerijesenih-predmeta-kazneni-traju-gotovo-1-000-dana/")
# htmltext = url.text

# f = open("html.txt", "w", encoding="utf-8")
# f.write(htmltext)
# f.close()

# word_list = get_clean_word_list(htmltext)
# parse_word_list(word_list)
# vector = get_vector(word_list)
# vector = get_sorted_dictionary(vector)
# print(vector)

# f = open("words.txt", "w", encoding="utf-8")
# f.write("\n".join(word_list))
# f.close()
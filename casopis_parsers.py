import requests

def get_document_content_from_24sata(link):
    content = ""

    html = requests.get(link).text

    div_level = 0
    article_start = html.find('<div class="article__content">')

    if article_start == -1:
        return "NOTHING"

    div_end = article_start
    while True:
        last_div_end = div_end
        div_end = html.find("</div>", div_end + 1)

        div_level = html.count("<div", last_div_end + 1, div_end)

        if div_level == 0:
            break

        while div_level > 1:
            div_end = html.find("</div>", div_end + 1)
            div_level -= 1

    html = html[article_start + len('<div class="article__content">') : div_end]

    paragraph_start = html.find("<p>")
    paragraph_end = html.find("</p>")
    while paragraph_start >= 0 and paragraph_end >= 0 and paragraph_end > paragraph_start:
        raw_text = html[paragraph_start + len("<p>") : paragraph_end].strip()
        content += raw_text
        content += "\n"

        paragraph_start = html.find("<p>", paragraph_end)
        paragraph_end = html.find("</p>", paragraph_start)


    # with open("temp/casopisi.txt", "a", encoding="utf-8") as file:
    #     file.write("\n")
    #     file.write(link)
    #     file.write(content)

    return content




def get_document_content_from_novilist(link):
    content = ""

    html = requests.get(link).text

    div_level = 0
    article_start = html.find('<div class="user-content">')

    if article_start == -1:
        return "NOTHING"

    div_end = article_start
    while True:
        last_div_end = div_end
        div_end = html.find("</div>", div_end + 1)

        div_level = html.count("<div", last_div_end + 1, div_end)

        if div_level == 0:
            break

        while div_level > 1:
            div_end = html.find("</div>", div_end + 1)
            div_level -= 1

    html = html[article_start + len('<div class="user-content">') : div_end]

    paragraph_start = html.find("<p>")
    paragraph_end = html.find("</p>")
    while paragraph_start >= 0 and paragraph_end >= 0 and paragraph_end > paragraph_start:
        raw_text = html[paragraph_start + len("<p>") : paragraph_end].strip()
        content += raw_text
        content += "\n"

        paragraph_start = html.find("<p>", paragraph_end)
        paragraph_end = html.find("</p>", paragraph_start)


    # with open("temp/casopisi.txt", "a", encoding="utf-8") as file:
    #     file.write("\n")
    #     file.write(link)
    #     file.write(content)

    return content
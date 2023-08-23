import requests

def get_document_content(link):
    content = ""
    div_class_name = ""

    try:
        html = requests.get(link).text
    except:
        print("Pogreška - nije moguće dohvatiti web-stranicu.")

    div_classes = {
        "https://www.24sata.hr": '<div class="article__content">',
        "https://www.novilist.hr": '<div class="user-content">',
        "https://hr.wikipedia.org": '<div id="mw-content-text"'
    }

    for domain in div_classes:
        if link.startswith(domain):
            div_class_name = div_classes[domain]
            break

    if div_class_name == "":
        return "NOTHING"

    div_level = 0
    article_start = html.find(div_class_name)

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

    html = html[article_start + len(div_class_name) : div_end]

    paragraph_start = html.find("<p>")
    paragraph_end = html.find("</p>")
    while paragraph_start >= 0 and paragraph_end >= 0 and paragraph_end > paragraph_start:
        raw_text = html[paragraph_start + len("<p>") : paragraph_end].strip()
        content += raw_text
        content += "\n"

        paragraph_start = html.find("<p>", paragraph_end)
        paragraph_end = html.find("</p>", paragraph_start)

    return content
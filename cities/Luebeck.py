from bs4 import BeautifulSoup
from util import convert_date

data_url = "http://kwlpls.adiwidjaja.info"
city_name = "Lübeck"
file_name = "Luebeck"

process_state_map = {
    "": "open",
    "Geöffnet": "open",
    "Vorübergehend geschlossen.": "closed",
    "Vorübergehend geschlossen": "closed",
    "Geschlossen": "closed"
}


def parse_html(html):
    soup = BeautifulSoup(html)

    data = {
        "last_updated": convert_date(soup.find("tr").find("strong").text, "Stand: %d.%m.%Y, %H:%M Uhr"),
        "lots": []
    }

    rows = soup.find_all("tr")
    rows = rows[1:]
    region_header = ""

    for row in rows:
        if len(row.find_all("th")) > 0:
            # This is a header row, save it for later
            region_header = row.find("th", {"class": "head1"}).text

        else:
            if row.find("td").text == "Gesamt":
                continue

            # This is a parking lot row
            raw_lot_data = row.find_all("td")

            if len(raw_lot_data) == 2:
                type_and_name = process_name(raw_lot_data[0].text)
                data["lots"].append({
                    "name": type_and_name[1],
                    "type": type_and_name[0],
                    "count": 0,
                    "free": 0,
                    "region": region_header,
                    "state": process_state_map.get(raw_lot_data[1].text, "")
                })

            elif len(raw_lot_data) == 4:
                type_and_name = process_name(raw_lot_data[0].text)
                data["lots"].append({
                    "name": type_and_name[1],
                    "type": type_and_name[0],
                    "count": int(raw_lot_data[1].text),
                    "free": int(raw_lot_data[2].text),
                    "region": region_header,
                    "state": "open"
                })

    return data


def process_name(name):
    lot_type = name[:2]
    lot_name = name[3:]

    type_mapping = {
        "PP": "Parkplatz",
        "PH": "Parkhaus",
    }
    if lot_type in type_mapping.keys():
        lot_type = type_mapping[lot_type]
    else:
        lot_type = ""

    return lot_type, lot_name

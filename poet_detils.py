import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

BASE_URL = "https://www.bangla-kobita.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def search_poet(poet_name):
    """
    Search poet and return profile url
    """

    params = {
        "q": poet_name
    }

    response = requests.get(
        f"{BASE_URL}/search/",
        params=params,
        headers=HEADERS
    )

    soup = BeautifulSoup(response.text, "html.parser")

    profile_tag = soup.select_one(
        'a[title^="Profile of"]'
    )

    if not profile_tag:
        return None

    href = profile_tag.get("href")

    return urljoin(BASE_URL, href)


def scrape_profile(profile_url):
    """
    Scrape profile page and return rows
    """

    response = requests.get(
        profile_url,
        headers=HEADERS
    )

    soup = BeautifulSoup(response.text, "html.parser")

    # -------------------
    # Profile Info
    # -------------------

    name = ""

    h1 = soup.find("h1")
    if h1:
        name = h1.get_text(strip=True)

    info = {
        "নাম": name,
        "জন্ম তারিখ": "",
        "জন্মস্থান": "",
        "বর্তমান নিবাস": "",
        "পেশা": "",
        "শিক্ষাগত যোগ্যতা": ""
    }

    for row in soup.find_all("tr"):

        cols = row.find_all(["th", "td"])

        if len(cols) < 2:
            continue

        key = cols[0].get_text(" ", strip=True)
        value = cols[1].get_text(" ", strip=True)

        if "জন্ম তারিখ" in key:
            info["জন্ম তারিখ"] = value

        elif "জন্মস্থান" in key:
            info["জন্মস্থান"] = value

        elif "বর্তমান নিবাস" in key:
            info["বর্তমান নিবাস"] = value

        elif "পেশা" in key:
            info["পেশা"] = value

        elif "শিক্ষাগত যোগ্যতা" in key:
            info["শিক্ষাগত যোগ্যতা"] = value

    # -------------------
    # Discussion Table
    # -------------------

    rows = []

    table = soup.find(
        "table",
        class_="post-list"
    )

    if not table:
        return rows

    for tr in table.select("tbody tr"):

        date_td = tr.find(
            "td",
            class_="DatePublished"
        )

        title_a = tr.select_one(
            "a.Title"
        )

        comment_td = tr.find(
            "td",
            class_="CommentCount"
        )

        if not (
            date_td and
            title_a and
            comment_td
        ):
            continue

        rows.append([
            info["নাম"],
            info["জন্ম তারিখ"],
            info["জন্মস্থান"],
            info["বর্তমান নিবাস"],
            info["পেশা"],
            info["শিক্ষাগত যোগ্যতা"],
            date_td.get_text(strip=True),
            title_a.get_text(strip=True),
            comment_td.get_text(strip=True)
        ])

    return rows


def save_csv(rows, filename="author_details.csv"):

    with open(
        filename,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "নাম",
            "জন্ম তারিখ",
            "জন্মস্থান",
            "বর্তমান নিবাস",
            "পেশা",
            "শিক্ষাগত যোগ্যতা",
            "তারিখ",
            "শিরোনাম",
            "মন্তব্য"
        ])

        writer.writerows(rows)


def main(poet_name):

    profile_url = search_poet(
        poet_name
    )

    if not profile_url:
        print("Poet not found")
        return

    print(
        f"Profile URL: {profile_url}"
    )

    rows = scrape_profile(
        profile_url
    )

    save_csv(rows)

    print(
        f"Saved {len(rows)} rows"
    )


if __name__ == "__main__":

    poet_name = input(
        "Enter poet name: "
    )

    main(poet_name)
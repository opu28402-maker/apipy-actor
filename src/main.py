import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import asyncio

# --------------------------------------------------
# Apify SDK (Python) ব্যবহার করার জন্য import
# --------------------------------------------------
from apify import Actor

BASE_URL = "https://www.bangla-kobita.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}


# --------------------------------------------------
# Function 1: কবির নাম দিয়ে Profile URL খোঁজা
# --------------------------------------------------
def search_poet(poet_name: str) -> str | None:
    """
    bangla-kobita.com-এ poet_name দিয়ে search করে
    প্রথম মিলে যাওয়া কবির Profile URL ফেরত দেয়।
    না পেলে None ফেরত দেয়।
    """
    params = {"q": poet_name}

    response = requests.get(
        f"{BASE_URL}/search/",
        params=params,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    profile_tag = soup.select_one('a[title^="Profile of"]')

    if not profile_tag:
        return None

    href = profile_tag.get("href")
    return urljoin(BASE_URL, href)


# --------------------------------------------------
# Function 2: Profile Page থেকে details scrape করা
# --------------------------------------------------
def scrape_profile(profile_url: str, max_poems: int = 0) -> list[dict]:
    """
    কবির Profile URL থেকে:
      - ব্যক্তিগত তথ্য (নাম, জন্মতারিখ, জন্মস্থান, ইত্যাদি)
      - কবিতার তালিকা (তারিখ, শিরোনাম, মন্তব্য সংখ্যা)
    scrape করে list of dict আকারে ফেরত দেয়।
    """

    response = requests.get(
        profile_url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # ---------- ব্যক্তিগত তথ্য ----------
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
        "শিক্ষাগত যোগ্যতা": "",
        "profile_url": profile_url
    }

    for row in soup.find_all("tr"):
        cols = row.find_all(["th", "td"])
        if len(cols) < 2:
            continue

        key   = cols[0].get_text(" ", strip=True)
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

    # ---------- কবিতার তালিকা ----------
    results = []

    table = soup.find("table", class_="post-list")
    if not table:
        # কবিতার table না পেলেও শুধু কবির info push করি
        results.append(info.copy())
        return results

    count = 0
    for tr in table.select("tbody tr"):

        if max_poems > 0 and count >= max_poems:
            break

        date_td    = tr.find("td", class_="DatePublished")
        title_a    = tr.select_one("a.Title")
        comment_td = tr.find("td", class_="CommentCount")

        if not (date_td and title_a and comment_td):
            continue

        row_data = info.copy()
        row_data.update({
            "কবিতার তারিখ": date_td.get_text(strip=True),
            "কবিতার শিরোনাম": title_a.get_text(strip=True),
            "কবিতার URL": urljoin(BASE_URL, title_a.get("href", "")),
            "মন্তব্য সংখ্যা": comment_td.get_text(strip=True)
        })

        results.append(row_data)
        count += 1

    return results


# --------------------------------------------------
# Actor Main Function
# --------------------------------------------------
async def main():
    async with Actor:

        # ---- Input পড়া ----
        actor_input = await Actor.get_input() or {}

        poet_names = actor_input.get("poet_names", [])
        max_poems  = actor_input.get("max_poems", 0)

        if not poet_names:
            Actor.log.warning("কোনো কবির নাম দেওয়া হয়নি! Input-এ poet_names দিন।")
            await Actor.set_value("OUTPUT", {
                "poetCount": 0,
                "totalPoems": 0,
                "datasetItemCount": 0,
                "failedPoets": []
            })
            return

        # ---- Tracking variables ----
        poet_count = 0
        total_poems = 0
        dataset_item_count = 0
        failed_poets = []

        # ---- Dataset খোলা (Apify Dataset-এ data save হবে) ----
        dataset = await Actor.open_dataset()

        for poet_name in poet_names:

            Actor.log.info(f"🔍 Searching: {poet_name}")

            # Step 1: Profile URL খোঁজা
            try:
                profile_url = search_poet(poet_name)
            except Exception as e:
                Actor.log.error(f"❌ Error searching {poet_name}: {e}")
                failed_poets.append(poet_name)
                continue

            if not profile_url:
                Actor.log.warning(f"❌ Poet not found: {poet_name}")
                await dataset.push_data({
                    "নাম": poet_name,
                    "error": "Poet not found on bangla-kobita.com"
                })
                failed_poets.append(poet_name)
                dataset_item_count += 1
                continue

            Actor.log.info(f"✅ Profile found: {profile_url}")

            # Step 2: Profile scrape করা
            try:
                rows = scrape_profile(profile_url, max_poems=max_poems)
            except Exception as e:
                Actor.log.error(f"❌ Error scraping {poet_name}: {e}")
                failed_poets.append(poet_name)
                continue

            # Step 3: Apify Dataset-এ push করা
            await dataset.push_data(rows)

            poet_count += 1
            total_poems += len(rows)
            dataset_item_count += len(rows)

            Actor.log.info(
                f"📦 {len(rows)} rows saved for poet: {poet_name}"
            )

        # ---- Output set করা (output_schema.json অনুযায়ী) ----
        output = {
            "poetCount": poet_count,
            "totalPoems": total_poems,
            "datasetItemCount": dataset_item_count,
            "failedPoets": failed_poets
        }

        await Actor.set_value("OUTPUT", output)

        Actor.log.info(
            f"🎉 Done! Poets: {poet_count}, "
            f"Poems: {total_poems}, "
            f"Failed: {len(failed_poets)}"
        )


# --------------------------------------------------
# Entry Point
# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())

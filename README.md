# Bangla Kobita Poet Details Scraper

**bangla-kobita.com** থেকে কবির নাম দিয়ে সার্চ করে কবির সম্পূর্ণ তথ্য ও কবিতার তালিকা scrape করে Apify Dataset-এ save করে।

---

## Input

| Field | Type | Required | Description |
|---|---|---|---|
| `poet_names` | `string[]` | ✅ হ্যাঁ | কবিদের নামের list (বাংলায় দিন) |
| `max_poems` | `integer` | না | প্রতি কবির সর্বোচ্চ কতটি কবিতা আনবে (0 = সব) |

### Input Example

```json
{
  "poet_names": ["রবীন্দ্রনাথ ঠাকুর", "কাজী নজরুল ইসলাম"],
  "max_poems": 10
}
```

---

## Output

Apify Dataset-এ প্রতিটি row-তে নিচের fields থাকবে:

| Field | Description |
|---|---|
| `নাম` | কবির নাম |
| `জন্ম তারিখ` | কবির জন্ম তারিখ |
| `জন্মস্থান` | কবির জন্মস্থান |
| `বর্তমান নিবাস` | বর্তমান বাসস্থান |
| `পেশা` | কবির পেশা |
| `শিক্ষাগত যোগ্যতা` | শিক্ষাগত যোগ্যতা |
| `profile_url` | কবির Profile URL |
| `কবিতার তারিখ` | কবিতা প্রকাশের তারিখ |
| `কবিতার শিরোনাম` | কবিতার নাম |
| `কবিতার URL` | কবিতার সরাসরি link |
| `মন্তব্য সংখ্যা` | কবিতায় মন্তব্যের সংখ্যা |

---

## Project Structure

```
apipy_actor/
├── .actor/
│   ├── actor.json          ← Actor metadata
│   └── input_schema.json   ← Input fields definition
├── src/
│   └── main.py             ← Actor main code
├── .gitignore
├── Dockerfile              ← Docker build file
├── README.md               ← এই file
└── requirements.txt        ← Python dependencies
```

---

## Local এ Test করার নিয়ম

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Apify CLI install করুন
npm install -g apify-cli

# 3. Local এ run করুন
apify run
```

---

## Apify Platform এ Deploy করার নিয়ম

```bash
# Login করুন
apify login

# Deploy করুন
apify push
```

Here’s a clean **setup guide** you can share with others so they can use your `ragformatter` workflow—but on **their own Apify account**, with **their own token**, and without affecting your tasks or usage.

---

## 📄 RAGFormatter Setup for Independent Use

This guide walks you through setting up `ragformatter`, a command-line tool to:

1. Fetch a sitemap
2. Filter and submit pages to Apify’s Website Content Crawler
3. Download the results
4. Feed the output into a local chunking pipeline for RAG systems

---

### ✅ Step 1: Clone the Crawler Task

1. **Sign up or log in** to Apify: [https://apify.com/](https://apify.com/)
2. Visit this public actor (used by `ragformatter`):
   👉 [https://apify.com/apify/website-content-crawler](https://apify.com/apify/website-content-crawler)
3. Click **“Try Actor”** → then **“Save as Task”**
4. Name it something like `rag-runner`
5. Set up any dummy input and click **Save**
6. Note your **task ID**, which will look like:

   ```
   your-username~rag-runner
   ```

---

### ✅ Step 2: Set Up Your Token

1. Go to: [https://console.apify.com/account/integrations](https://console.apify.com/account/integrations)
2. Copy your **API token**
3. Add it to your environment:

#### Option A: Add to `~/.zshrc` or `~/.bashrc`

```bash
export APIFY_TOKEN="your-actual-token-here"
```

Then run:

```bash
source ~/.zshrc  # or ~/.bashrc
```

#### Option B: Use a `.env` file

```env
APIFY_TOKEN=your-actual-token-here
```

Make sure this is in the same directory as `ragformatter.py`.

---

### ✅ Step 3: Download the Script

Download `ragformatter.py` from Colin (or this repo). Place it in your project folder or install globally.

Update this line near the top of the script:

```python
ACTOR_TASK_ID = "your-username~rag-runner"
```

---

### ✅ Step 4: Install Dependencies

From your project folder (ideally inside a virtualenv):

```bash
pip install -r requirements.txt
```

**Minimal requirements:**

```
requests
python-dotenv
beautifulsoup4
```

---

### ✅ Step 5: Run It

```bash
python3 ragformatter.py https://docs.example.com/sitemap.xml guides examples/setup
```

This will:

* Parse the sitemap
* Filter to matching URLs
* Submit the crawl job
* Wait for it to finish
* Download the results to `ingestion_source/`
* Automatically trigger your local RAG pipeline

---

### ✅ Optional: Make It Global

Add this to your `~/.zshrc`:

```bash
alias ragformatter='python3 /path/to/your/ragformatter.py'
```

---

Let me know if you want this turned into a sharable PDF or Markdown file.

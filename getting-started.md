# 🧠 RAGFormatter Setup Guide

This guide helps you run `ragformatter.py` with your own **Apify account**, **API token**, and **pipeline setup**, entirely independent from Colin's environment.

Repo URL: https://github.com/auldsyababua/Anything_To_RAG_Format

---

## 🚀 What Is RAGFormatter?

`ragformatter.py` is a CLI script that:

1. Parses a sitemap
2. Sends URLs to Apify’s **Website Content Crawler** via a direct Actor POST
3. Waits for the crawl to finish
4. Downloads the results to `ingestion_source/`
5. Triggers the full local RAG preprocessing pipeline (`make run`)

---

## ✅ Step 1: Get Your Apify API Token

1. Log in to [apify.com](https://apify.com/)
2. Go to your profile → **Integrations**
3. Copy your **API token**

You don’t need to clone or save a task — the actor is called directly via `run-sync`.

---

## ✅ Step 2: Set Up Your `.env`

Create a `.env` file at the repo root:

```env
APIFY_TOKEN=your_apify_token_here
REPO_ROOT=/absolute/path/to/repo/root
OUTPUT_ROOT=/absolute/path/to/desired/output/dir
````

These values are used by `config.py` and all scripts.

> 💡 `REPO_ROOT` points to the codebase
> 💡 `OUTPUT_ROOT` holds your pipeline outputs (cleaned, split, validated)

---

## ✅ Step 3: Install Everything

```bash
make install
```

This creates a virtualenv and installs all dependencies from `requirements.txt`.

---

## ✅ Step 4: Run It!

```bash
python3 ragformatter.py https://docs.example.com/sitemap.xml
```

This will:

* Parse the sitemap
* POST the URLs directly to the Apify actor
* Download the structured crawl results
* Trigger `make run` to clean, split, and validate

You’ll get:

* `doc-lib/full/unified-clean.json`
* `doc-lib/split/{domain}.json` (or multiple parts if >50MB)

---

## ✅ Optional: Shell Alias

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias ragformatter='python3 /absolute/path/to/ragformatter.py'
```

Then:

```bash
source ~/.zshrc
ragformatter https://docs.example.com/sitemap.xml
```

---

## ✅ Output Structure

```bash
OUTPUT_ROOT/
├── full/
│   └── unified-clean.json
├── split/
│   └── yourdomain.json
└── ...
```

---

## ✅ Recovery Shortcut

If your crawl finishes but `ragformatter.py` crashes or times out:

```bash
recover_apify_run <RUN_ID>
make post
```

This will:

* Download the finished run’s dataset
* Save it to `ingestion_source/recovered_crawl.json`
* Resume the pipeline at post-ingest stages

---

## ✅ For Collaborators

* Use `.env.example` to share the setup
* Keep `.env` private — it’s gitignored
* All pipeline behavior is driven by `REPO_ROOT`, `OUTPUT_ROOT`, and the Makefile

---

## ✅ VSCode Task Integration (Optional)

If you use VSCode, define tasks for one-click execution:

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run RAG Pipeline",
      "type": "shell",
      "command": "make run",
      "group": "build"
    },
    {
      "label": "Recover Apify Run",
      "type": "shell",
      "command": "recover_apify_run ${input:runId}",
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    }
  ],
  "inputs": [
    {
      "id": "runId",
      "type": "promptString",
      "description": "Enter Apify Run ID"
    }
  ]
}
```

Now run:

```
Cmd+Shift+P → Tasks: Run Task → “Run RAG Pipeline” or “Recover Apify Run”
```

---

## ✅ Quickstart Recap

```bash
# Setup
make install
cp .env.example .env  # edit paths + token

# Crawl + process
python3 ragformatter.py https://example.com/sitemap.xml

# Recovery if timeout
recover_apify_run <RUN_ID>
make post
```

Output:

```
full/unified-clean.json
split/<domain>.json
```

Now you’re ready to embed them into any RAG pipeline.

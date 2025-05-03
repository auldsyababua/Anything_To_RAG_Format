# 🧠 RAGFormatter Setup Guide

This guide helps you run `ragformatter.py` with your own **Apify account**, **API token**, and **pipeline setup**, entirely independent from Colin's environment.

Repo URL: https://github.com/auldsyababua/Anything_To_RAG_Format

---

## 🚀 What Is RAGFormatter?

`ragformatter.py` is a CLI script that:

1. Parses a sitemap
2. Sends URLs to Apify’s Website Content Crawler
3. Waits for the crawl to finish
4. Downloads the results to `ingestion_source/`
5. Triggers the full local RAG preprocessing pipeline

---

## ✅ Step 1: Clone the Apify Task

1. Sign in to [apify.com](https://apify.com/)
2. Visit the actor page:  
   👉 https://apify.com/apify/website-content-crawler
3. Click **“Try Actor”** → **“Save as Task”**
4. Name the task `rag-runner` or similar
5. Save it (you can use any sample input)
6. Copy your task ID:

```text
your-username~rag-runner
````

---

## ✅ Step 2: Set Up Your `.env`

Create a `.env` file at the repo root (same level as `ragformatter.py`):

```env
APIFY_TOKEN=your_apify_token_here
REPO_ROOT=/absolute/path/to/clean-gpt-json
OUTPUT_ROOT=/absolute/path/to/doc-lib
```

These are used by `config.py` and all pipeline scripts.

---

## ✅ Step 3: Update the Script

In `ragformatter.py`, make sure this constant is correct:

```python
ACTOR_TASK_ID = "your-username~rag-runner"
```

---

## ✅ Step 4: Install Everything

Set up the environment:

```bash
make install
```

This creates a virtualenv and installs all dependencies from `requirements.txt`.

---

## ✅ Step 5: Run It!

```bash
python3 ragformatter.py https://docs.example.com/sitemap.xml
```

This will:

* Parse the sitemap
* Crawl the pages
* Download the structured content
* Feed it into `make run`

You’ll get final output like:

* `doc-lib/full/unified-clean.json`
* `doc-lib/split/unraid-docs.json` (or multiple if >50MB)
* Schema-validated, title-injected, size-checked chunks

---

## ✅ (Optional) Shell Alias

Add this to your `~/.zshrc` or `~/.bashrc`:

```bash
alias ragformatter='python3 /absolute/path/to/ragformatter.py'
```

Reload your shell:

```bash
source ~/.zshrc
```

Now you can run:

```bash
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

If your Apify crawl finishes but the local script crashes:

```bash
recover_apify_run <RUN_ID>
```

This will:

* Download the results
* Save to `ingestion_source/recovered_crawl.json`
* Resume the pipeline via `make post`

---

## ✅ For Collaborators

* Use `.env.example` to share the setup
* Keep real tokens in `.env` (gitignored)
* Set paths using `REPO_ROOT` and `OUTPUT_ROOT`
* All Make targets are defined in the `Makefile`

Great — here's the **VSCode Tasks + Quickstart section** to add at the bottom of your `getting-started.md`:

---

## ✅ VSCode Task Integration (Optional)

If you're using VSCode, you can define custom tasks to trigger the pipeline directly from the Command Palette or sidebar.

1. Create `.vscode/tasks.json`:

```
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run RAG Pipeline",
      "type": "shell",
      "command": "make run",
      "group": "build",
      "problemMatcher": []
    },
    {
      "label": "Recover Apify Run",
      "type": "shell",
      "command": "recover_apify_run ${input:runId}",
      "problemMatcher": [],
      "dependsOn": [],
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
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
````

2. Now run:

* `Cmd+Shift+P` → `Tasks: Run Task` → Select `Run RAG Pipeline` or `Recover Apify Run`

---

## ✅ Quickstart Recap

```
# Setup
make install
cp .env.example .env  # edit paths + token

# Crawl + process
python3 ragformatter.py https://example.com/sitemap.xml

# Recovery if timeout
recover_apify_run <RUN_ID>
make post
```

# Final files in OUTPUT_ROOT:
# full/unified-clean.json
# split/<domain>.json

---


# Docker Usage Guide

This guide explains how to build and run the UMinho DSpace 8 scraper inside a Docker container.
The container bundles **Python 3.11**, **Chromium**, and the matching **ChromeDriver** so you do not need to install any of these on your host machine.

---

## Prerequisites

| Tool | Minimum version | Install link |
|------|----------------|--------------|
| Docker Engine | 24+ | <https://docs.docker.com/engine/install/> |
| Docker Compose | 2.x (`docker compose`) | Included with Docker Desktop |

> **Note:** Docker Desktop (Windows / macOS) ships both tools in one installer.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/uminho-biomed-pri/IR-class-project.git
cd IR-class-project
```

### 2. Build the image

```bash
docker build -t uminho-scraper .
```

This single command:
- Pulls `python:3.11-slim` as the base image
- Installs `chromium` and `chromium-driver` (version-matched by the Debian package manager)
- Installs all Python dependencies listed in `requirements.txt`
- Copies the application source code into the image

### 3. Run the scraper

```bash
docker run --rm --name scraper uminho-scraper
```

The container will:
1. Launch Chrome in headless mode (no visible window)
2. Scrape the configured UMinho repository collection
3. Save the results to `scraper_results.json` inside the container

### 4. Retrieve the output file

Because the output is written inside the container, copy it to your host machine:

```bash
# Run without --rm so the container persists after it finishes
docker run --name scraper uminho-scraper

# Copy the result file to the current directory on your host
docker cp scraper:/app/scraper_results.json ./scraper_results.json

# Clean up the stopped container
docker rm scraper
```

---

## Using Docker Compose

Docker Compose provides a convenient shortcut.

### Build and run

```bash
docker compose up --build
```

### Run only (if image is already built)

```bash
docker compose up
```

### Retrieve the output file after the container finishes

```bash
docker cp uminho-scraper:/app/scraper_results.json ./scraper_results.json
```

### Remove the container

```bash
docker compose down
```

---

## Customising the Scraper

To change the target collection or the maximum number of items, edit `main.py` **before** building the image:

```python
collection = "1822/21293"       # change to any DSpace collection handle
scraper_instance = scraper.UMinhoDSpace8Scraper(base_url, max_items=50)
```

Then rebuild:

```bash
docker build -t uminho-scraper .
```

---

## Running Tests

The test suite can be executed inside the container as well:

```bash
docker run --rm uminho-scraper pytest
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `WebDriverException: unknown error: cannot find Chrome binary` | Old layer cached without Chromium | Rebuild with `docker build --no-cache -t uminho-scraper .` |
| Scraper hangs / timeout | Network issue reaching repositorium.uminho.pt | Check host internet access; VPN may be required |
| `Permission denied` when copying output | Container already removed (`--rm` flag) | Re-run without `--rm` and then use `docker cp` |

---

## Container Details

| Property | Value |
|----------|-------|
| Base image | `python:3.11-slim` (Debian Bookworm) |
| Browser | Chromium (installed via `apt`) |
| WebDriver | `chromium-driver` (version-matched by apt) |
| Python dependencies | `selenium`, `pytest`, `pytest-cov` |
| Working directory | `/app` |
| Output file | `/app/scraper_results.json` |

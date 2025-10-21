name: PowerUpStack Upload

on:
  push:
    branches:
      - main

jobs:
  upload:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install selenium pillow

      - name: Download ChromeDriver
        run: |
          sudo apt-get update
          sudo apt-get install -y chromium-browser chromium-chromedriver
          echo "ChromeDriver installed."

      - name: Run upload script
        env:
          PUP_USER: ${{ secrets.PUP_USER }}
          PUP_PASS: ${{ secrets.PUP_PASS }}
        run: |
          python3 scripts/powerup_upload.py

      - name: Commit screenshots
        run: |
          git config --local user.name "github-actions[bot]"
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git add screenshots/*.png || true
          git commit -m "Add Selenium screenshots [CI]" || echo "No changes to commit"
          git push || echo "Nothing to push"

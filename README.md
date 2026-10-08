# California's Working Landscapes dashboard

An interactive companion to the UC ANR report *California's Working Landscapes:
Evolving Contributions to National, State, and Regional Economies* (2025).
Built with [Streamlit](https://streamlit.io).

## Put it online (about 10 minutes, no coding)

### 1. Put this folder on GitHub

1. Go to <https://github.com/new>.
2. Name the repository `working-landscapes-dashboard`, choose **Public**, and
   click **Create repository**. Leave every other box unticked.
3. On the next page click the link **uploading an existing file**.
4. Open this folder on your computer, select **everything inside it**
   (`app.py`, `common.py`, `requirements.txt`, `README.md`, and the `views`,
   `data` and `docs` folders) and drag it all onto the GitHub page.
5. Click **Commit changes**.

Check: the repository's front page should list `app.py` at the top level, not
inside another folder.

One file needs a separate step, because your Mac hides folders that start with
a dot. It sets the colors and is optional (the app works without it):

1. In the repository click **Add file → Create new file**.
2. In the name box type `.streamlit/config.toml`.
3. Paste in the contents of the `config.toml` file below, then **Commit changes**.

```toml
[theme]
base = "light"
primaryColor = "#256abf"
backgroundColor = "#fcfcfb"
secondaryBackgroundColor = "#f0efec"
textColor = "#0b0b0b"
```

### 2. Launch it on Streamlit

1. Go to <https://share.streamlit.io> and sign in.
2. Click **Create app**, then **Deploy a public app from GitHub**.
3. Fill in:
   - **Repository:** `your-github-name/working-landscapes-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** pick something short, e.g. `ca-working-landscapes`
4. Click **Deploy**. After two or three minutes the app opens at
   `https://<the-name-you-picked>.streamlit.app`. That is the link to share
   or embed on your website.

### Changing it later

Edit or re-upload a file on GitHub and the live app updates itself within a
minute. No need to redeploy.

## Try it on your own computer first (optional)

In Terminal, from inside this folder:

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

It opens in your browser at <http://localhost:8501>. Press Ctrl+C in Terminal
to stop it.

## What is in this folder

| File | What it does |
|---|---|
| `app.py` | Starting point: the page menu and the Jobs / Sales / Earnings / Businesses switch |
| `common.py` | Shared wording, colors, number formatting and chart helpers. Most text edits happen here. |
| `views/overview.py` | Overview page |
| `views/place.py` | Your county or region |
| `views/compare.py` | Compare places (ranked list and county map) |
| `views/segments.py` | Segments and the nation |
| `views/about.py` | About the data |
| `data/` | Four small CSV files and the county map outline that the app reads |
| `docs/DESIGN.md` | The design brief the app was built from |
| `requirements.txt` | Tells Streamlit which Python packages to install |

## Updating the data

The CSVs in `data/` are made from the original spreadsheets by
`Code/prepare_data.py`, which lives one level up, outside this folder (the
raw spreadsheets are not uploaded). After changing a spreadsheet, run
`python Code/prepare_data.py` from the main project folder, then upload the
refreshed `data/` files to GitHub.

## Common text edits

- Segment descriptions: `SEGMENT_ABOUT` in `common.py`.
- Definitions of the four measures: `MEASURES` in `common.py`.
- Segment colors: `SEGMENT_COLORS` in `common.py`.
- Link to the report: `REPORT_URL` in `common.py`.

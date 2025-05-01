#  YouTube Leads Categorization

This script analyzes YouTube channels to determine their recent video upload frequency and classifies their activity level, paying special attention to YouTube Shorts uploads. It processes a list of channel URLs from input CSV files and outputs the results, including a classification label and a potential TikTok search link, into a single `output.csv` file.

This categorization tool processes a CSV file of YouTube channel leads. For an effective workflow to generate this input CSV by filtering and selecting channels directly from YouTube search results, consider using the youtube_lead_getter Chrome extension: https://github.com/AbdelftahZowail/youtube_lead_getter


## Features

*   **Bulk Channel Analysis:** Processes multiple YouTube channel URLs provided in `.csv` files.
*   **Recent Activity Focus:** Analyzes video uploads within the last 3 months.
*   **Shorts Detection:** Uses the YouTube Data API v3 to check for recent Shorts uploads.
*   **Classification:** Categorizes channels based on upload frequency and Shorts activity (`posts shorts`, `maybe later`, `Sample`, `inconsistent`, `probably stopped`).
*   **TikTok Link Generation:** Creates a potential TikTok search URL for channels classified as `maybe later` or `Sample`.
*   **CSV Input/Output:** Reads channel URLs from any `.csv` file in the script's directory (except `output.csv`) and writes results to `output.csv`.
*   **Hybrid Approach:** Uses `scrapetube` for general video counts (reducing API quota usage) and the official YouTube Data API v3 for specific Shorts data.

## Prerequisites

*   **Python 3.x**
*   **Google API Client Library for Python:** Used for interacting with the YouTube Data API v3.
*   **scrapetube:** Used for efficiently scraping channel video information without relying solely on the API.
*   **YouTube Data API v3 Key:** You need API credentials from Google Cloud Console to query Shorts information.

## Installation

1.  **Clone or Download:** Get the `main.py` script.
    ```bash
    # If using git
    git clone <repository_url>
    cd <repository_directory>
    ```
    Or simply download the `main.py` file.

2.  **Install Dependencies:**
    ```bash
    pip install google-api-python-client scrapetube
    ```

## Configuration

1.  **YouTube Data API v3 Key:**
    *   Obtain an API key from the [Google Cloud Console](https://console.cloud.google.com/). You'll need to create a project and enable the "YouTube Data API v3".
    *   **IMPORTANT:** Open `main.py` and add your API key(s) to the `apis` list:
        ```python
        # main.py
        apis = ['YOUR_API_KEY_HERE', 'ANOTHER_API_KEY_IF_NEEDED'] # Replace with your actual key(s)
        ```
    *   **Security Warning:** Avoid committing your API keys directly into version control (like Git) if you plan to share this code. Consider using environment variables or a separate configuration file for better security practices.

2.  **Input CSV Files:**
    *   Prepare one or more `.csv` files containing the YouTube channel URLs you want to analyze.
    *   Each CSV file **must** have a header row.
    *   One of the columns **must** be named exactly `URL` and contain the full URL of the YouTube channels (e.g., `https://www.youtube.com/@MrBeast`, `https://www.youtube.com/channel/UC[...]`).
    *   Place these input `.csv` files in the **same directory** as the `main.py` script. Any `.csv` file in the directory *except* `output.csv` will be treated as input.

## Usage

1.  Ensure your API key(s) are added to the `apis` list in `main.py`.
2.  Ensure your input `.csv` files (with the `URL` column) are in the same directory as `main.py`.
3.  Run the script from your terminal:
    ```bash
    python main.py
    ```
4.  The script will prompt you to select which API key from the `apis` list to use (enter the index number, starting from 0).
    ```
    which api? 0
    ```
5.  The script will then process each URL from the input CSV files. Progress and any errors will be printed to the console. Example output line per channel:
    ```
    Channel: Example Channel (https://www.youtube.com/@example/videos) | Last 3 months: [5, 3, 1] | Label: inconsistent
    Channel: Shorts Creator (https://www.youtube.com/@shortscreator/shorts) | Last 3 months: [10, 8, 6] | Label: maybe later | TikTok: https://www.tiktok.com/search?q=Shorts%20Creator
    ```
6.  Once finished, the script will print `all done` and wait for you to press Enter before exiting.
7.  A new file named `output.csv` will be created (or overwritten) in the same directory, containing the analysis results.

## Output Format (`output.csv`)

The output CSV file will contain the following columns:

*   **Channel Name:** The name of the YouTube channel.
*   **Channel URL:** The original channel URL, appended with `/videos` or `/shorts` based on the classification logic.
*   **Label:** The classification assigned by the script:
    *   `probably stopped`: Fewer than 5 videos uploaded in the last 3 months.
    *   `posts shorts`: 12+ videos in the last 3 months, and the last 3 Shorts were all uploaded within the last 7 days.
    *   `maybe later`: 12+ videos in the last 3 months, and the last 3 Shorts were all uploaded within the last 30 days (but not all within the last 7).
    *   `Sample`: 12+ videos in the last 3 months, but the last 3 Shorts don't fit the criteria for `posts shorts` or `maybe later` (or no Shorts found).
    *   `inconsistent`: Between 5 and 11 videos (inclusive) uploaded in the last 3 months.
*   **TikTok URL:** A URL to search TikTok for the channel name (generated only if the label is `maybe later` or `Sample`). This is a search link, *not* a guaranteed link to the correct TikTok profile.

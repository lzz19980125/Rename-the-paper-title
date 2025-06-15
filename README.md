# Rename-the-paper-title
A simple Python script to automatically rename your academic papers based on their actual titles.



## The Problem

When you download many academic papers from sites like arXiv, IEEE Xplore, or Elsevier, the filenames are often cryptic and uninformative, like `2203.10135.pdf` or `download.pdf`. This makes organizing and finding the paper you need a real hassle.

## The Solution

This tool scans a folder of PDF files, intelligently extracts the real title from each paper, and renames the file accordingly.

**Before:**

*   `1706.03762.pdf`
*   `main.pdf`

**After:**

*   `Attention Is All You Need.pdf`
*   `A Novel Framework for Few-Shot Learning.pdf`

## Features

*   **Two-Step Title Extraction:** First, it tries the fast and reliable method of reading the title from the PDF's metadata.
*   **Intelligent Content Analysis:** If no metadata is found, it analyzes the text on the first page. It identifies the title by finding the text with the largest font size, which is a common characteristic of paper titles.
*   **Smart Exception Handling:** It cleverly handles cases where the largest text isn't the title. For example, on many arXiv or Elsevier papers, the journal name or a "Peer Review" stamp is the largest text. In these situations, the script automatically uses the text with the *second-largest* font size, which is almost always the correct title.
*   **Clean Filenames:** It automatically removes characters that are illegal in filenames (like `\`, `/`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) to ensure compatibility.
*   **Handles Duplicates:** If two papers happen to have the same title, it prevents overwriting by adding a suffix like `(1)`, `(2)`, etc., to the filename.

## How It Works

The script uses a two-pronged approach to find a paper's title:

1.  **Check Metadata (via `PyPDF2`):** It first opens the PDF and looks for the "Title" field in its document information. If a title is present, it uses it. This is the quickest and most accurate method.

2.  **Analyze Page Content (via `PyMuPDF`):** If the metadata is empty, the script performs a more advanced analysis on the first page of the PDF:
    *   It extracts all text elements along with their font sizes and positions.
    *   It assumes the title is the text written in the **largest font**.
    *   It contains special rules for common publishers. For instance, if the largest text is a known journal name (e.g., "Knowledge-Based Systems", "Information Sciences") or a generic term like "arxiv", it correctly assumes the real title is the text with the **second-largest font size**.

This heuristic-based approach is highly effective for most academic papers from popular sources.

## Installation

This script requires Python 3 and a couple of libraries. You can install the dependencies using pip.

```bash
pip install PyPDF2 PyMuPDF
```

## Usage

1.  Place the `rename_all_pdf.py` script in the folder containing the PDF files you want to rename.

2.  Open your terminal or command prompt.

3.  Run the script, telling it to process the current directory (`.`):

    ```bash
    python rename_all_pdf.py ./pdf_file_folder
    ```

The script will now go through each PDF, print its progress, and rename the files.

## Contributing

Contributions are welcome! If you have ideas for improving the title extraction logic or adding new features, feel free to fork the repository and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

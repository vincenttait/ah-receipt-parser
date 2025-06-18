
# Albert Heijn Receipt Parser

## Project Summary

This repository contains a complete pipeline for extracting structured data from Albert Heijn (AH) grocery receipts. It performs PDF OCR, text parsing, and tabular formatting, ultimately producing a clean dataset suitable for price analysis, personal inflation tracking, or downstream economic modeling.

This project wasn’t designed to be a general-purpose receipt parser. It’s built around one use case: parsing real receipts from AH under realistic conditions, using minimal setup, and producing output you can actually analyze.

## Problem Background

Inflation in the Netherlands, especially that of groceries, often feels higher than official numbers suggest. CBS and ECB statistics provide national and continental averages, but these don’t reflect what individual consumers experience.

Albert Heijn is the largest supermarket chain in the country, and it’s also the one I use most frequently. While AH offers digital receipts through their app, they come as PDFs without searchable text. There’s no easy way to get structured product-level data out of them.

To make any kind of personal analysis possible, I needed a way to:
1. OCR the raw PDF.
2. Parse the messy extracted text into structured rows.
3. Store it all in a usable dataset.

This pipeline does exactly that.

## Pipeline Overview

### Receipt Ingestion
- Works with PDFs downloaded from the AH mobile app.
- Reads from `data/receipts/person1/` and `person2/`.
- Assigns a `person` label to each row based on the folder structure.
- Designed to parse receipts for both myself and my girlfriend.
- If you want to add more people, you’ll need to adapt the logic in `build_dataset.py`.

### OCR (Text Extraction)
- Converts PDF pages to images using `pdf2image`.
- Applies Tesseract OCR with the following config: `custom_oem_psm_config = '--oem 3 --psm 6'`.
  This treats the page as one dense block instead of trying to segment layout. It gave much better results on AH’s format.

### Text Parsing
- Extracts:
  - Product name
  - Units purchased
  - Total price
  - Discount flag (B or BB)
  - Timestamp
  - Source file path
- Handles AH-specific quirks like bonus flags at line ends.
- Uses simple regex and line structure detection, no external dependencies beyond OCR.

### Output
- Combines all results into a single dataset.
- Writes to `data/processed/all_receipts.csv` using `|` as a delimiter.
- Each row is tagged with the `person` it came from.

## Key Decisions and Pitfalls

### Tesseract Config Tuning
Initial attempts using default OCR config failed to detect bonus labels (B / BB). Several other page segmentation modes led to misaligned columns or dropped data. Because of that we settled on `--oem 3 --psm 6` after testing. No structure inference, just raw text block parsing.

### Store Address Extraction
I initially planned to include store addresses and postcodes, similar to how timestamps are extracted. But this data was too inconsistently placed, sometimes on multiple lines, sometimes missing altogether. Since AH has uniform pricing across stores, it shouldn't matter for the purposes of inflation analysis.

### Multi-Person Support
Receipts are sorted into two folders: one for me, one for my girlfriend. The pipeline then tracks whose receipt each row came from using folder name detection. If you add more folders, you’ll need to extend this in the code manually.

## Repository Layout

```
src/
├── build_dataset.py         # Main runner: processes all receipts into one CSV
├── parsing/
│   ├── extract_text.py      # OCR logic (PDF to text)
│   └── parse_text.py        # Text to structured product info

data/
├── receipts/                # Input PDFs (excluded)
│   ├── person1/
│   └── person2/
└── processed/               # Output CSVs (excluded)
```

## Quickstart
This project requires [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) to be installed and available in your system path.  
Follow the install instructions on their GitHub page for your operating system.

```bash
git clone https://github.com/vincenttait/ah-receipt-parser.git
cd ah-receipt-parser

python -m venv .venv
.\.venv\Scripts ctivate

pip install -r requirements.txt
python -m src.build_dataset
```

To test:
- Drop a few PDFs into data/receipts/person1/
- Run the command above
- Check data/processed/all_receipts.csv

## Sample Output

| product_name | price_total | units | discount_flag | timestamp           | source_file                       | person   |
|--------------|-------------|-------|----------------|----------------------|-----------------------------------|----------|
| BROOD WIT    | 1.29        | 1     | None           | 2024-03-12 17:25     | data/receipts/person1/receipt.pdf | person1  |
| AH COLA      | 0.99        | 2     | B              | 2024-03-12 17:25     | data/receipts/person1/receipt.pdf | person1  |

## Potential Extensions

### Personal CPI Tracking
Build a personal inflation index weighted by your own basket.

### Location-Based Analysis
Even though AH has fixed prices, there’s still value in knowing where purchases occurred. Possible use cases:
- Mapping store visit frequency
- Linking store ID to in-app promotions
- Identifying travel patterns

### Misc Ideas
- Add CLI usage (parse one receipt on demand).
- Group near-duplicate product names using string similarity.
- Visualize monthly spending by category.

## License

MIT License. See LICENSE file.

import re
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.parsing.extract_text import extract_text_psm6

def parse_text_from_receipt(filepath: Path) -> pd.DataFrame:
    """
    Parse product lines from an AH receipt PDF into a DataFrame.

    Extracts product name, price, quantity, discount type, timestamp, and source file.
    """
    text = extract_text_psm6(filepath)
    lines = text.split("\n")

    # --- Timestamp Extraction ---
    timestamp = None
    for line in lines:
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})', line)
        time_match = re.search(r'(\d{1,2}:\d{2})', line)
        if date_match and time_match:
            try:
                date_str = date_match.group(1).replace('/', '-')
                time_str = time_match.group(1)
                timestamp = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
                break
            except ValueError:
                continue

    # --- Product Line Extraction ---
    products = []
    inside_block = False

    for line in map(str.strip, lines):
        if "AANTAL OMSCHRIJVING" in line.upper():
            inside_block = True
            continue

        if inside_block and "SUBTOTAAL" in line.upper() and not line.upper().startswith("BONUS"):
            break

        if not inside_block or line.startswith("+"):
            continue

        match = re.match(r"(\d+)\s+(.+?)\s+(\d{1,5}(?:,\d{2})?)(?:\s+(B{1,2}))?$", line)
        if match:
            quantity = int(match.group(1))
            product_name = re.sub(r"[^a-zA-Z\s]", "", match.group(2)).strip()
            price_raw = match.group(3)
            discount_flag = match.group(4) if match.group(4) else None

            # Normalize price
            price_total = float(price_raw.replace(",", ".")) if "," in price_raw else float(
                price_raw[:-2] + '.' + price_raw[-2:]
            )

            products.append({
                "product_name": product_name,
                "price_total": price_total,
                "units": quantity,
                "discount_flag": discount_flag,
                "timestamp": timestamp,
                "source_file": str(filepath)
            })

    return pd.DataFrame(products)

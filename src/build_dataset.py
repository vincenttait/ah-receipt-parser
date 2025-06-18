import os
import pandas as pd
from pathlib import Path

from src.parsing.parse_text import parse_text_from_receipt

def process_folder(folder_path: Path) -> pd.DataFrame:
    """
    Process all PDF receipts in a given folder.

    Args:
        folder_path (Path): Path to folder containing PDFs.

    Returns:
        pd.DataFrame: Parsed receipt lines as DataFrame.
    """
    dfs = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            file_path = folder_path / file
            print(f"Parsing: {file_path}")
            try:
                df = parse_text_from_receipt(file_path)
                dfs.append(df)
            except Exception as e:
                print(f"❌ Error parsing {file_path}: {e}")

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def build_full_dataset():
    """
    Process all receipts from both persons and save a combined CSV.
    """
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data" / "receipts"
    output_dir = base_dir / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    person1_df = process_folder(data_dir / "person1")
    person2_df = process_folder(data_dir / "person2")

    full_df = pd.concat([person1_df, person2_df], ignore_index=True)

    full_df["person"] = full_df["source_file"].apply(
        lambda x: "person1" if "person1" in x.lower() else "person2"
    )

    output_path = output_dir / "all_receipts.csv"
    full_df.to_csv(output_path, index=True, sep="|")
    print(f"✅ Extraction complete. Saved to {output_path.relative_to(base_dir)}")

if __name__ == "__main__":
    build_full_dataset()

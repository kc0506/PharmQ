from functools import cache
from pathlib import Path
from typing import Dict

import pandas as pd

from ..models.category import Category


@cache
def load_csv_data(
    data_dir: str = str(Path(__file__).parent / "../data"),
) -> Dict[str, Category]:
    """Load all CSV files from the data directory using pandas."""
    categories = {}
    data_path = Path(data_dir)

    for csv_file in data_path.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file)
            if df.empty:
                continue

            category_name = csv_file.stem
            answer_column = df.columns[0]  # First column is the answer
            fields = [col for col in df.columns if col != answer_column]

            categories[category_name] = Category(
                id=category_name, data=df, fields=fields
            )
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")

    return categories

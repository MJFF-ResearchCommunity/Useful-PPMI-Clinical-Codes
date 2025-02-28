import os
import glob
import re
import pandas as pd

#function for importing files based on prefix
#this future proofs for future updates with different date suffixes
def get_latest_file(prefix, ext=".csv", directory="../data/"):
    """
    Finds the most recent file with the given prefix and extension.
    """
    print(f"Looking for files in: {directory}")

    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist.")

    # Search for files matching the pattern
    pattern = os.path.join(directory, f"{prefix}_*{ext}")
    files = glob.glob(pattern)
    
    print(f"Found files: {files}")  # Debugging output

    if not files:
        raise FileNotFoundError(f"No files found matching {prefix}_*.{ext} in {directory}")

    # Extract date using regex and sort
    def extract_date(filename):
        match = re.search(r"(\d{2}[A-Za-z]{3}\d{4})", filename)  # Looks for "27Feb2025"
        return match.group(1) if match else ""

    files.sort(key=extract_date, reverse=True)
    
    latest_file = files[0]
    print(f"Latest file: {latest_file}")
    return latest_file

#manually handles non-numeric values
def safe_to_numeric(column):
    try:
        return pd.to_numeric(column)
    except ValueError:
        return column  # Return the original column if conversion fails
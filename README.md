# DAA_PBL Project

## Overview
This project processes and analyzes FIR (First Information Report) data using various tools and algorithms. It includes functionalities for:

1. **Pattern Matching with KMP Algorithm**: Searches for specific patterns in FIR descriptions and filters rows based on matches.
2. **Text Formatting with Gemma API**: Converts unstructured FIR descriptions into structured formats using the Gemma API.
3. **Environment Configuration**: Uses `dotenv` for secure API key management.

---

## Features

### 1. KMP Algorithm for Pattern Matching
- File: `KMP.py`
- Reads FIR data from a CSV file.
- Searches for user-provided patterns in the `Formatted` column.
- Outputs a new CSV file containing rows that match the pattern.

## Setup

### Prerequisites
- Python 3.8+
- Install required packages:
  ```bash
  pip install -r requirements.txt
  ```


### Input Files
- `synthetic_fir1.csv`: Contains FIR data with a `Formatted` column for pattern matching.

---

## Usage

### 1. Run KMP Pattern Matching
```bash
python3 KMP.py
```
- Enter the pattern to search when prompted.
- The filtered rows will be saved to `filtered_fir.csv`.
---

## Project Structure
```
DAA_PBL/
├── KMP.py                # KMP algorithm for pattern matching
├── synthetic_fir1.csv    # Input FIR data
├── filtered_fir.csv      # Output of KMP pattern matching
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## License
This project is licensed under the MIT License.

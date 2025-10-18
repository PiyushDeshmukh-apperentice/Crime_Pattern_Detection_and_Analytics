import csv

def computeLPS(pat, M, lps):
    # handle empty pattern
    if M == 0:
        return
    length = 0
    i = 1
    lps[0] = 0
    while i < M:
        if pat[i] == pat[length]:
            lps[i] = length + 1
            length += 1
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

def KMP(pat, s):
    # both pat and s are expected to be already normalized (lowercase)
    M = len(pat)
    # empty pattern: treat as match
    if M == 0:
        return True
    N = len(s)
    lps = [0] * M
    computeLPS(pat, M, lps)

    i = 0  # string pointer
    j = 0  # pattern pointer
    while i < N:
        if pat[j] == s[i]:
            i += 1
            j += 1
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

        if j == M:
            return True  # Pattern found
            j = lps[j - 1]

    return False  # Pattern not found

def filter_csv_by_pattern(input_csv, output_csv, pattern):
    # normalize pattern to lowercase and strip whitespace
    pattern = (pattern or "").strip().lower()
    with open(input_csv, mode='r', encoding='utf-8') as infile, open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in reader:
            formatted = (row.get('Formatted') or "").lower()
            if KMP(pattern, formatted):
                writer.writerow(row)

if __name__ == "__main__":
    input_csv = "/mnt/StorageHDD/Projects/DAA_PBL/synthetic_fir1.csv"
    output_csv = "filtered_fir.csv"
    pattern = input("Enter the pattern to search: ")
    pattern = (pattern or "").strip().lower()
    filter_csv_by_pattern(input_csv, output_csv, pattern)
    print(f"Filtered rows saved to {output_csv}")

import csv

def computeLPS(pat, M, lps):
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
    M = len(pat)
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
    with open(input_csv, mode='r') as infile, open(output_csv, mode='w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in reader:
            if KMP(pattern, row['Formatted']):
                writer.writerow(row)

if __name__ == "__main__":
    input_csv = "/home/piyush/Desktop/Projects/DAA_PBL/synthetic_fir1.csv"
    output_csv = "filtered_fir.csv"
    pattern = input("Enter the pattern to search: ")
    filter_csv_by_pattern(input_csv, output_csv, pattern)
    print(f"Filtered rows saved to {output_csv}")

# Email Cleaning and Hashing Utility

This utility performs the cleaning and hashing of email addresses. It correctes common typos in domains and TLDs, standardizes equivalent domains, and outputs MD5 hashes for the cleaned email addresses. This can be useful for data normalization and privacy purposes before storing or using email addresses in datasets.

## Description

The program can process individual email addresses provided via command line or batches of email addresses from a CSV file. The script corrects known typos (e.g., "gmai.com" to "gmail.com"), normalizes domains according to predefined rules, and computes the MD5 hash of each resulting address.

Reference data is retrieved from the accompanying `reference_data.py`, which contains mappings for typo corrections and domain equivalences, including a large set of Fastmail and Yahoo domains.

This code base was adapted from maxmind's minfraud python client.  
https://github.com/maxmind/minfraud-api-python
Details of the clean/normalization process ar described here:
https://dev.maxmind.com/minfraud/normalizing-email-addresses-for-minfraud

## Getting Started

### Dependencies

- Python 3.x
- hashlib (for MD5 hashing, included in Python's standard library)

### Installing

- Clone the repository or download the source files to your local machine.
- Ensure Python 3.x is installed on your system.

### Executing program

- To clean and hash an individual email address, use:
```bash
python clean_email_hash.py --email example@gmail.com
```
- To process a list of email addresses from a CSV file:
```bash
python clean_email_hash.py --file emails.csv --outf emails_hashed.csv
```
- If your CSV does not have headers, include the `--no_header` flag.
- To include extra columns from the input file in the output, add the `--output_non_email_columns` flag.
- To output the email addresses before and after cleaning (contains sensitive data, use with caution), add the `--include_emails` flag.

### CSV File Format

For processing CSV files, the input CSV is expected to have email addresses in the first column. If `--output_non_email_columns` is used, the remaining columns will be included in the output unchanged.

## Help

Use `python clean_email_hash.py -h` to see a help message and understand the usage of additional command-line arguments.

## License

This project is licensed under the [MIT License](LICENSE.md) - see the LICENSE.md file for details.

## Acknowledgments

- The email cleaning logic was inspired by MaxMind's open-source MinFraud API client.
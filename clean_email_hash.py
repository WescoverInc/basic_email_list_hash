"""This utility cleans up and hashes email lists

   The below code was adapted from maxmind's minfraud python client.
   
   https://github.com/maxmind/minfraud-api-python
   Details of the clean/normalization process ar described here:
   https://dev.maxmind.com/minfraud/normalizing-email-addresses-for-minfraud
"""

import re
import hashlib
import unicodedata
import argparse
import csv

from reference_data import (
    _TYPO_DOMAINS,
    _TYPO_TLDS,
    _EQUIVALENT_DOMAINS,
    _YAHOO_DOMAINS,
    _FASTMAIL_DOMAINS,
)

def hash_csv_file(
    csv_file_path,
    out_file_path=None,
    no_header=False,
    output_non_email_columns=True,
    include_emails=False,
):
    """Hash email addresses in a CSV file"""
    out_data = []
    with open(csv_file_path, "r", newline="") as csv_file:
        if no_header:
            csv_reader = csv.reader(csv_file)
            headers = None
        else:
            csv_reader = csv.DictReader(csv_file)
            headers = csv_reader.fieldnames
            output_emails_header = ["hashed_email"]
            output_others_header = headers[1:]

            if include_emails:
                output_emails_header.append("clean_email")
                output_emails_header.append("original_email")

        for row in csv_reader:
            email = row[0] if no_header else row.get(headers[0])
            hashed_email, clean_email = hash_clean_email(email)
            hashed_email = hashed_email or "n/a"
            clean_email = clean_email or "n/a"
            if no_header:
                output_emails = [hashed_email]
                if include_emails:
                    output_emails.append(clean_email)
                    output_emails.append(email)

                output = (
                    [*output_emails, *row[1:]]
                    if output_non_email_columns
                    else output_emails
                )
                out_data.append(output_emails + row[1:])
            else:
                output = {
                    "hashed_email": hashed_email,
                }
                if include_emails:
                    output["clean_email"] = clean_email
                    output["original_email"] = email

                out_data.append(
                    {
                        **output,
                        **{
                            k: v
                            for k, v in row.items()
                            if output_non_email_columns and k in output_others_header
                        },
                    }
                )

    out_file_path = out_file_path or csv_file_path.replace(".csv", "_hashed.csv")

    with open(out_file_path, mode="w", newline="") as file:
        if no_header:
            csv_writer = csv.writer(file)
        else:
            headers = output_emails_header
            if output_non_email_columns:
                headers = headers + output_others_header
            csv_writer = csv.DictWriter(file, fieldnames=headers)
            csv_writer.writeheader()

        csv_writer.writerows(out_data)

    print(f"Hashed {len(out_data)} rows to output file: {out_file_path}")


def hash_clean_email(raw_email_address):
    """Hash email address if present"""
    if raw_email_address is None:
        return None, None

    address, _ = _clean_email(raw_email_address)
    if address is None:
        return None, None

    return hashlib.md5(address.encode("UTF-8")).hexdigest(), address


def _clean_domain(domain):
    domain = domain.strip().rstrip(".").encode("idna").decode("ASCII")

    domain = re.sub(r"(?:\.com){2,}$", ".com", domain)
    domain = re.sub(r"^\d+(?:gmail?\.com)$", "gmail.com", domain)

    idx = domain.rfind(".")
    if idx != -1:
        tld = domain[idx + 1 :]  # noqa
        if tld in _TYPO_TLDS:
            domain = domain[:idx] + "." + _TYPO_TLDS.get(tld)

    domain = _TYPO_DOMAINS.get(domain, domain)
    domain = _EQUIVALENT_DOMAINS.get(domain, domain)

    return domain


def _clean_email(address):
    address = address.lower().strip()

    at_idx = address.rfind("@")
    if at_idx == -1:
        return None, None

    domain = _clean_domain(address[at_idx + 1 :])  # noqa
    local_part = address[:at_idx]

    local_part = unicodedata.normalize("NFC", local_part)

    # Strip off aliased part of email address.
    if domain in _YAHOO_DOMAINS:
        divider = "-"
    else:
        divider = "+"

    alias_idx = local_part.find(divider)
    if alias_idx > 0:
        local_part = local_part[:alias_idx]

    if domain == "gmail.com":
        local_part = local_part.replace(".", "")

    domain_parts = domain.split(".")
    if len(domain_parts) > 2:
        possible_domain = ".".join(domain_parts[1:])
        if possible_domain in _FASTMAIL_DOMAINS:
            domain = possible_domain
            if local_part != "":
                local_part = domain_parts[0]

    return f"{local_part}@{domain}", domain


if __name__ == "__main__":
    # define args for the command line usage
    parser = argparse.ArgumentParser(description="Clean and hash email addresses")
    parser.add_argument("--email", "-e", help="Email address to clean and hash")
    parser.add_argument(
        "--file",
        "-f",
        help="Email address inputs csv file to clean and hash, expects first column to be the input email address, other columns are left as-is or ignored",
    )
    parser.add_argument(
        "--no_header",
        help="Expect no input/output CSV headers",
        action="store_true",
    )
    parser.add_argument("--outf", "-o", help="Output file name")
    parser.add_argument(
        "--output_non_email_columns",
        help="Output columns found after the first column - untouched",
        action="store_true",
    )
    parser.add_argument(
        "--include_emails",
        help="Output also the email before/after cleaning (sensitive data)",
        action="store_true",
    )

    parser.epilog = """Example: python clean_email.py --email example@gmail.com
or python clean_email.py --file emails.csv --outf emails_hashed.csv
    """

    args = parser.parse_args()

    if args.email is not None:
        email_hash, email_clean = hash_clean_email(args.email)
        print(f"hash: {email_hash}, clean: {email_clean}")
    elif args.file is not None:
        hash_csv_file(
            args.file,
            no_header=args.no_header,
            out_file_path=args.outf,
            output_non_email_columns=args.output_non_email_columns,
            include_emails=args.include_emails,
        )
    else:
        print("No email address provided")
        print(parser.print_help())

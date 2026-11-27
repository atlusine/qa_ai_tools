"""Email the daily bug re-check report.

Sends the chat summary as the message body and the HTML report (plus any
screenshots) as attachments. Standard library only.

Settings come from environment variables, never from the repo:
  BUG_RETEST_EMAIL_TO  recipients, comma-separated (required)
  SMTP_USER            sender account, for Gmail your address (required)
  SMTP_PASSWORD        for Gmail an app password, not your normal password (required)
  SMTP_HOST            default smtp.gmail.com
  SMTP_PORT            default 465 (SSL)

Usage:
  python send_report.py --report bug-recheck-2026-11-27.html \
      --summary summary.txt [--attach shots/*.png] [--dry-run]
"""

import argparse
import glob
import mimetypes
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path


def build_message(report: Path, summary: str, attachments: list[Path], sender: str, recipients: list[str]) -> EmailMessage:
    first_line = summary.strip().splitlines()[0] if summary.strip() else f"Bug re-check: {report.stem}"
    msg = EmailMessage()
    msg["Subject"] = first_line[:150]
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(summary + "\n\nThe full report is attached (open the .html file in a browser).\n")
    for path in [report, *attachments]:
        ctype, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)
    return msg


def main() -> int:
    parser = argparse.ArgumentParser(description="Email the bug re-check report.")
    parser.add_argument("--report", required=True, help="Path to the HTML report")
    parser.add_argument("--summary", required=True, help="Path to a text file with the chat summary")
    parser.add_argument("--attach", nargs="*", default=[], help="Extra files or globs, e.g. screenshots")
    parser.add_argument("--dry-run", action="store_true", help="Build the email and print its headers; send nothing")
    args = parser.parse_args()

    report = Path(args.report)
    summary_path = Path(args.summary)
    for path in (report, summary_path):
        if not path.is_file():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2
    attachments = [Path(p) for pattern in args.attach for p in sorted(glob.glob(pattern)) if Path(p).is_file()]

    recipients = [r.strip() for r in os.environ.get("BUG_RETEST_EMAIL_TO", "").split(",") if r.strip()]
    sender = os.environ.get("SMTP_USER", "")
    missing = [name for name, value in (("BUG_RETEST_EMAIL_TO", recipients), ("SMTP_USER", sender)) if not value]
    if not args.dry_run and not os.environ.get("SMTP_PASSWORD"):
        missing.append("SMTP_PASSWORD")
    if missing:
        print("ERROR: not set: " + ", ".join(missing) + ". See the 'Email' section of the daily-bug-retest skill.", file=sys.stderr)
        return 2

    msg = build_message(report, summary_path.read_text(encoding="utf-8-sig"), attachments, sender, recipients)

    if args.dry_run:
        files = ", ".join(p.name for p in [report, *attachments])
        print(f"DRY RUN, not sent.\nTo: {msg['To']}\nSubject: {msg['Subject']}\nAttachments: {files}")
        return 0

    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    try:
        with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=30) as smtp:
            smtp.login(sender, os.environ["SMTP_PASSWORD"])
            smtp.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        # Never print the password; the exception text does not contain it.
        print(f"ERROR: email not sent: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Sent to {msg['To']}: {msg['Subject']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

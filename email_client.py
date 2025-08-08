import imaplib
import smtplib
import email
from email.message import EmailMessage


class SimpleEmailClient:
    """Minimal email client for sending and fetching messages."""

    def __init__(self, imap_server: str, smtp_server: str, address: str, password: str):
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.address = address
        self.password = password

    def send_email(self, to_address: str, subject: str, body: str) -> None:
        """Send an email via SMTP."""
        msg = EmailMessage()
        msg["From"] = self.address
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL(self.smtp_server) as smtp:
            smtp.login(self.address, self.password)
            smtp.send_message(msg)

    def fetch_inbox_headers(self):
        """Fetch sender and subject for all messages in INBOX."""
        headers = []
        with imaplib.IMAP4_SSL(self.imap_server) as imap:
            imap.login(self.address, self.password)
            imap.select("INBOX")
            status, data = imap.search(None, "ALL")
            if status != "OK":
                return headers
            for num in data[0].split():
                status, msg_data = imap.fetch(num, "(RFC822)")
                if status != "OK":
                    continue
                msg = email.message_from_bytes(msg_data[0][1])
                headers.append({"from": msg.get("From"), "subject": msg.get("Subject")})
        return headers


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simple command line email client")
    parser.add_argument("--imap", required=True, help="IMAP server hostname")
    parser.add_argument("--smtp", required=True, help="SMTP server hostname")
    parser.add_argument("--address", required=True, help="Email address")
    parser.add_argument("--password", required=True, help="Password")

    subparsers = parser.add_subparsers(dest="command")

    send_parser = subparsers.add_parser("send")
    send_parser.add_argument("to")
    send_parser.add_argument("subject")
    send_parser.add_argument("body")

    fetch_parser = subparsers.add_parser("fetch")

    args = parser.parse_args()

    client = SimpleEmailClient(args.imap, args.smtp, args.address, args.password)

    if args.command == "send":
        client.send_email(args.to, args.subject, args.body)
        print("Email sent!")
    elif args.command == "fetch":
        headers = client.fetch_inbox_headers()
        for h in headers:
            print(f"From: {h['from']} | Subject: {h['subject']}")
    else:
        parser.print_help()

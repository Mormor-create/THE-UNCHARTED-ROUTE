import imaplib
import logging
import os
import re
from datetime import datetime, timezone
from email import message_from_bytes
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from html.parser import HTMLParser
from extensions import db
from app.models.contact import Contact
from app.models.contact_reply import ContactReply

logger = logging.getLogger(__name__)

class _HTMLTextExtractor(HTMLParser):
    """Convert HTML email content into readable text."""

    BLOCK_TAGS = {
        "address", "article", "br", "div", "footer", "h1", "h2",
        "h3", "h4", "header", "li", "p", "section", "table",
        "td", "th", "tr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "head"}:
            self.hidden_depth += 1
        elif self.hidden_depth == 0 and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "head"} and self.hidden_depth:
            self.hidden_depth -= 1
        elif self.hidden_depth == 0 and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.hidden_depth == 0:
            self.parts.append(data)

    def get_text(self):
        text = "".join(self.parts)
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line).strip()


class ContactMailboxSyncService:
    """Synchronize incoming Gmail replies with CMS contact conversations."""

    @staticmethod
    def _decode_header_value(value):
        if not value:
            return ""

        parts = []
        for part, encoding in decode_header(value):
            if isinstance(part, bytes):
                parts.append(
                    part.decode(encoding or "utf-8", errors="replace")
                )
            else:
                parts.append(part)

        return "".join(parts).strip()

    @staticmethod
    def _extract_body(message):
        """Extract readable email text without importing attachments."""

        plain_parts = []
        html_parts = []

        parts = message.walk() if message.is_multipart() else [message]

        for part in parts:
            if part.get_content_maintype() == "multipart":
                continue

            if part.get_content_disposition() == "attachment":
                continue

            content_type = part.get_content_type()
            if content_type not in {"text/plain", "text/html"}:
                continue

            payload = part.get_payload(decode=True)
            if payload is None:
                continue

            charset = part.get_content_charset() or "utf-8"

            try:
                content = payload.decode(charset, errors="replace").strip()
            except (LookupError, UnicodeError):
                content = payload.decode("utf-8", errors="replace").strip()

            if not content:
                continue

            if content_type == "text/plain":
                plain_parts.append(content)
            elif content_type == "text/html":
                html_parts.append(content)

        if plain_parts:
            return "\n\n".join(plain_parts).strip()

        if html_parts:
            extractor = _HTMLTextExtractor()
            try:
                for html in html_parts:
                    extractor.feed(html)
                extractor.close()
                return extractor.get_text()
            except Exception:
                logger.exception("Could not extract text from HTML email.")

        return ""

    @staticmethod
    def _normalize_subject(subject):
        subject = (subject or "").strip()

        while True:
            cleaned = re.sub(
                r"^\s*((re|fw|fwd)\s*:\s*)",
                "",
                subject,
                flags=re.IGNORECASE,
            )
            if cleaned == subject:
                break
            subject = cleaned

        return " ".join(subject.casefold().split())

    @classmethod
    def _find_contact(cls, sender_email, subject, message):
        """
        Match an email to an existing contact.

        Priority:
        1. Stored Message-ID referenced by the incoming email.
        2. Unique sender + original enquiry subject.
        3. Unique sender + a subject stored in that conversation.
        """

        sender_email = (sender_email or "").strip().casefold()
        normalized_subject = cls._normalize_subject(subject)

        references = (
            (message.get("In-Reply-To") or "")
            + " "
            + (message.get("References") or "")
        )
        referenced_ids = re.findall(r"<[^<>\s]+>", references)

        # First attempt: use the stored email-thread references.
        if referenced_ids:
            referenced_replies = ContactReply.query.filter(
                ContactReply.email_message_id.in_(referenced_ids)
            ).all()

            referenced_contacts = {}
            for reply in referenced_replies:
                if reply.contact is not None:
                    referenced_contacts[reply.contact.id] = reply.contact

            # Do not attach to an unrelated or ambiguous conversation.
            matching_referenced_contacts = [
                contact
                for contact in referenced_contacts.values()
                if (contact.email or "").strip().casefold() == sender_email
                and not contact.is_archived
            ]

            if len(matching_referenced_contacts) == 1:
                return matching_referenced_contacts[0]

        if not sender_email or not normalized_subject:
            return None

        # Only consider active enquiries belonging to this sender.
        candidates = Contact.query.filter(
            db.func.lower(Contact.email) == sender_email,
            Contact.is_archived.is_(False),
        ).all()

        if not candidates:
            return None

        # Match against both the original enquiry subject and subjects
        # already stored in each conversation.
        candidate_ids = [contact.id for contact in candidates]

        saved_replies = ContactReply.query.filter(
            ContactReply.contact_id.in_(candidate_ids)
        ).all()

        subjects_by_contact = {
            contact.id: {
                cls._normalize_subject(contact.subject)
            }
            for contact in candidates
        }

        for reply in saved_replies:
            if reply.subject:
                subjects_by_contact.setdefault(
                    reply.contact_id, set()
                ).add(cls._normalize_subject(reply.subject))

        matching = [
            contact
            for contact in candidates
            if normalized_subject in subjects_by_contact.get(
                contact.id, set()
            )
        ]

        # Never guess if multiple conversations have the same subject.
        if len(matching) == 1:
            return matching[0]

        return None

    @classmethod
    def sync_inbox(cls):
        """Import incoming messages from the configured IMAP mailbox."""

        username = os.getenv("IMAP_USERNAME")
        password = os.getenv("IMAP_PASSWORD")
        server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        port = int(os.getenv("IMAP_PORT", "993"))
        folder = os.getenv("IMAP_FOLDER", "INBOX")

        if not username or not password:
            raise RuntimeError(
                "IMAP_USERNAME and IMAP_PASSWORD must be configured."
            )

        imported = 0
        skipped = 0
        unmatched = 0
        mailbox = None

        try:
            mailbox = imaplib.IMAP4_SSL(server, port)
            mailbox.login(username, password)

            status, _ = mailbox.select(folder)
            if status != "OK":
                raise RuntimeError(
                    f"Could not open mailbox folder: {folder}"
                )

            status, result = mailbox.uid("search", None, "ALL")
            if status != "OK":
                raise RuntimeError("Could not search the mailbox.")

            uids = result[0].split()

            for uid in uids:
                status, data = mailbox.uid(
                    "fetch", uid, "(BODY.PEEK[])"
                )

                if status != "OK" or not data:
                    skipped += 1
                    logger.debug("Skipping mailbox UID %s: fetch failed.", uid)
                    continue

                raw_email = next(
                    (
                        item[1]
                        for item in data
                        if isinstance(item, tuple) and item[1]
                    ),
                    None,
                )

                if not raw_email:
                    skipped += 1
                    logger.debug(
                        "Skipping mailbox UID %s: no message payload.", uid
                    )
                    continue

                message = message_from_bytes(raw_email)
                message_id = (message.get("Message-ID") or "").strip()

                if not message_id:
                    skipped += 1
                    logger.debug(
                        "Skipping mailbox UID %s: missing Message-ID.", uid
                    )
                    continue

                # Prevent importing the same message more than once.
                if ContactReply.query.filter_by(
                    email_message_id=message_id
                ).first():
                    skipped += 1
                    logger.debug(
                        "Skipping %s: Message-ID already exists.", message_id
                    )
                    continue

                sender_name, sender_email = parseaddr(
                    message.get("From", "")
                )
                sender_email = sender_email.strip().casefold()

                # Ignore messages sent by the business mailbox.
                if sender_email == username.strip().casefold():
                    skipped += 1
                    logger.debug(
                        "Skipping %s: sent by the business mailbox.",
                        message_id,
                    )
                    continue

                subject = cls._decode_header_value(
                    message.get("Subject", "")
                )
                body = cls._extract_body(message)

                if not body:
                    skipped += 1
                    logger.debug(
                        "Skipping %s: no readable message body.",
                        message_id,
                    )
                    continue

                contact = cls._find_contact(
                    sender_email, subject, message
                )

                if contact is None:
                    unmatched += 1
                    logger.warning(
                        "Incoming email could not be matched: "
                        "message_id=%r, sender=%r, subject=%r, "
                        "in_reply_to=%r, references=%r",
                        message_id,
                        sender_email,
                        subject,
                        message.get("In-Reply-To"),
                        message.get("References"),
                    )
                    continue

                # Defensive sender check before attaching to a conversation.
                if (
                    (contact.email or "").strip().casefold()
                    != sender_email
                ):
                    unmatched += 1
                    logger.warning(
                        "Rejected email %s: sender does not match "
                        "contact %s.",
                        message_id,
                        contact.id,
                    )
                    continue

                received_at = datetime.now(timezone.utc).replace(
                    tzinfo=None
                )
                date_header = message.get("Date")

                if date_header:
                    try:
                        parsed_date = parsedate_to_datetime(date_header)
                        if parsed_date:
                            if parsed_date.tzinfo is None:
                                parsed_date = parsed_date.replace(
                                    tzinfo=timezone.utc
                                )
                            received_at = parsed_date.astimezone(
                                timezone.utc
                            ).replace(tzinfo=None)
                    except (TypeError, ValueError, OverflowError):
                        logger.debug(
                            "Could not parse Date header for %s.",
                            message_id,
                        )

                reply = ContactReply(
                    contact_id=contact.id,
                    user_id=None,
                    sender_name=sender_name or sender_email,
                    sender_email=sender_email,
                    subject=subject or contact.subject or "Email reply",
                    message=body,
                    delivery_method="Email",
                    delivery_status="Received",
                    direction="incoming",
                    email_message_id=message_id,
                    received_at=received_at,
                )

                db.session.add(reply)
                db.session.flush()
                imported += 1

                logger.info(
                    "Imported incoming email %s into contact %s.",
                    message_id,
                    contact.id,
                )

            db.session.commit()

            return {
                "imported": imported,
                "skipped": skipped,
                "unmatched": unmatched,
            }

        except Exception:
            db.session.rollback()
            logger.exception("Contact mailbox synchronization failed.")
            raise

        finally:
            if mailbox is not None:
                try:
                    mailbox.logout()
                except Exception:
                    pass

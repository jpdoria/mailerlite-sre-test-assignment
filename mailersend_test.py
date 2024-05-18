from mailersend import emails


def handle_email():
    """
    Process the email resource.
    """
    api_token = "mlsn.123"
    mailer = emails.NewEmail(api_token)

    # Define an empty dict to populate with mail values
    mail_body = {}

    mail_from = {
        "name": "jp",
        "email": "jp@konsol.sh",
    }

    recipients = [
        {
            "name": "root",
            "email": "root@konsol.sh",
        }
    ]

    reply_to = [
        {
            "name": "jp",
            "email": "jp@konsol.sh",
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Hello!", mail_body)
    mailer.set_html_content("This is the HTML content", mail_body)
    mailer.set_plaintext_content("This is the text content", mail_body)
    mailer.set_reply_to(reply_to, mail_body)

    # Using print() will also return status code and data
    print(mailer.send(mail_body))


if __name__ == "__main__":
    handle_email()

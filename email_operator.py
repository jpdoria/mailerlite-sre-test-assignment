import base64

import kopf
import kubernetes.client as k8s_client
from kubernetes.client.rest import ApiException
from mailersend import emails


def get_secret(api, namespace, secret_name):
    """
    Get the MailerSend API token from the secret.
    """
    try:
        secret = api.read_namespaced_secret(secret_name, namespace)
        return secret
    except ApiException as e:
        raise kopf.PermanentError(f"Failed to get secret: {e}")


@kopf.on.create("konsol.sh", "v1", "emailsenderconfigs")
@kopf.on.update("konsol.sh", "v1", "emailsenderconfigs")
def handle_emailsenderconfig(meta, spec, status, namespace, logger, **kwargs):
    """
    Log the creation or update of EmailSenderConfig.
    """
    logger.info(f"EmailSenderConfig {meta['name']} created or updated")


@kopf.on.create("konsol.sh", "v1", "emails")
def handle_email(meta, spec, status, namespace, logger, patch, **kwargs):
    """
    Process the email resource.
    """
    api = k8s_client.CoreV1Api()

    # Fetch the EmailSenderConfig
    sender_config_name = spec["senderConfigRef"]
    try:
        sender_config = k8s_client.CustomObjectsApi().get_namespaced_custom_object(
            group="konsol.sh",
            version="v1",
            namespace=namespace,
            plural="emailsenderconfigs",
            name=sender_config_name,
        )
    except ApiException as e:
        logger.error(f"Failed to get EmailSenderConfig: {e}")
        patch.status["deliveryStatus"] = "Failed"
        patch.status["error"] = str(e)
        return

    # Fetch the API token from the secret
    secret_name = sender_config["spec"]["apiTokenSecretRef"]
    secret = get_secret(api, namespace, secret_name)
    api_token = base64.b64decode(secret.data["apiToken"]).decode("utf-8")
    mailer = emails.NewEmail(api_token)

    # Define an empty dict to populate with mail values
    mail_body = {}

    mail_from = {
        "name": sender_config["spec"]["senderEmail"].split("@")[0],
        "email": sender_config["spec"]["senderEmail"],
    }

    recipients = [
        {
            "name": spec["recipientEmail"].split("@")[0],
            "email": spec["recipientEmail"],
        }
    ]

    reply_to = [
        {
            "name": sender_config["spec"]["senderEmail"].split("@")[0],
            "email": sender_config["spec"]["senderEmail"],
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Hello!", mail_body)
    mailer.set_html_content("This is the HTML content", mail_body)
    mailer.set_plaintext_content("This is the text content", mail_body)
    mailer.set_reply_to(reply_to, mail_body)

    # Using print() will also return status code and data
    mailer.send(mail_body)


if __name__ == "__main__":
    kopf.run()

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId
from ics import Calendar, Event
import base64
import json

from email.utils import formatdate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from services.secrets import SecretService

secret = SecretService(f"email/{os.environ.get('env', 'dev')}/api")


class MailSender:
    api_key = None
    from_email = None

    templates = {
        'roster': 'd-000f5ba606324814b0cf316d98ffb59f'
    }

    def __init__(self, **kwargs):
        self.api_key = secret.get()['api_key']
        self.from_email = kwargs.get('from_email', secret.get()['from_email'])

    def email(self, to_email, template, data):
        # We always append on the destination url to help.
        data['url'] = secret.get()['url']

        # Build the mail object & send the email.

        # Attach the ics to the email
        c = generate_ics()

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email)
        message.dynamic_template_data = data
        message.template_id = self.templates[template]

        encoded = base64.b64encode(str(c).encode('utf-8')).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType('text/calendar')
        attachment.file_name = FileName('shift.ics')
        attachment.disposition = Disposition('attachment')
        attachment.content_id = ContentId('Example Content ID')
        message.attachment = attachment

        try:
            sendgrid_client = SendGridAPIClient(api_key=self.api_key)
            response = sendgrid_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)


def generate_ics():
    c = Calendar()
    e = Event()
    e.name = "Fireapp shift details: "
    e.begin = '2021-01-01 00:00:00'
    e.end = '2021-05-01 00:00:00'
    c.events.add(e)
    return c


sender = MailSender()
# generate_ics()

# sender.email(['vganearachchi@gmail.com'], 'roster', {
#     'startTime': '11:30am 4 Apr 2020',
#     'endTime': '11:30am 4 Apr 2020',
#     'role': 'Driver',
#     'url': "https://test.com"
# })

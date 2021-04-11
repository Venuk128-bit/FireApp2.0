import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from ics import Calendar, Event
import base64

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
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            html_content='<strong>This will be replaced by your template.</strong>')
        message.dynamic_template_data = data
        message.template_id = self.templates[template]
        # Attach the ics to the email
        generate_ics()
        file_path = 'shift.ics'
        with open(file_path, 'rb') as f:
            data = f.read()
            f.close()
        encoded = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType('application/ics')
        attachment.file_name = FileName('your_shift.ics')
        attachment.disposition = Disposition('attachment')
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
    with open('shift.ics', 'w') as my_file:
        my_file.writelines(c)


sender = MailSender()
# generate_ics()

sender.email(['vganearachchi@gmail.com'], 'roster', {
    'startTime': '11:30am 4 Apr 2020',
    'endTime': '11:30am 4 Apr 2020',
    'role': 'Driver',
    'url': "https://test.com"
})

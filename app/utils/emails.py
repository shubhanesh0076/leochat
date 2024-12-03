import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Optional, Protocol
from jinja2 import Environment, FileSystemLoader
from utils import settings as st

# Step 1: Define SMTP Configuration
class SMTPConfig:
    def __init__(
        self, smtp_server: str, smtp_port: int, from_email: str, smtp_passwd: str
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.smtp_passwd = smtp_passwd

    def get_smtp_server(self):
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.from_email, self.smtp_passwd)
            return server
        
        except Exception as e:
            print("Errro: ", e)
            raise ConnectionError(f"Error in SMTP configuration: {e}")


# Step 2: Define a Protocol for email templates (Interface Segregation)
class EmailTemplateProtocol(Protocol):
    def render(self, context: Dict[str, str]) -> str: ...

# Step 3: Create EmailTemplate class to handle content
class EmailTemplate:
    def __init__(self, template_file: str, template_dir: Optional[str] = None):
        template_dir = template_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "templates", "emails")
        )
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template_file = template_file
        
    def render(self, context: Dict[str, str]) -> str:
        try:
            template = self.env.get_template(self.template_file)
            return template.render(context)

        except Exception as e:
            raise ValueError(f"Error rendering template: {e}")


# Step 4: Define Mailer class for sending emails
class Mailer:
    def __init__(self, smtp_config: SMTPConfig):
        self.smtp_config = smtp_config
        self.server = None

    def send_email(
        self, to_emails: List[str], subject: str, email_content: str
    ) -> Dict[str, str]:
        try:
            self.server = self.smtp_config.get_smtp_server()

            msg = MIMEMultipart()
            msg["From"] = self.smtp_config.from_email
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = subject
            msg.attach(MIMEText(email_content, "html"))

            self.server.sendmail(
                self.smtp_config.from_email, to_emails, msg.as_string()
            )
            return {"status": "success", "message": "Email sent successfully."}
        except Exception as e:
            return {"status": "failure", "message": f"Failed to send email: {e}"}
        finally:
            if self.server:
                self.server.quit()


# Step 5: Define a higher-level EmailService class for different types of emails
class EmailService:
    def __init__(self, mailer: Mailer, template: EmailTemplate):
        self.mailer = mailer
        self.template = template

    def send_simple_email(
        self, to_emails: List[str], context: Dict[str, str], subject: str
    ) -> Dict[str, str]:
        # subject = "Welcome to Leo Chat"
        
        email_content = self.template.render(context)
        send_email_to_user = self.mailer.send_email(to_emails, subject, email_content)
        return send_email_to_user

    def send_login_alert_email(
        self, to_emails: List[str], context: Dict[str, str], subject: str
    ) -> Dict[str, str]:
        # subject = "New Login Alert"
        email_content = self.template.render(context)
        return self.mailer.send_email(to_emails, subject, email_content)


def simple_mailer(template_file: str, context, to_emails, subject):

    smtp_config = SMTPConfig(
        smtp_server=st.EMAIL_HOST,
        smtp_port=st.EMAIL_PORT,
        from_email=st.EMAIL_HOST_USER,
        smtp_passwd=st.EMAIL_HOST_PASSWORD,
    )
    mailer = Mailer(smtp_config)
    
    # For a registration email
    registration_template = EmailTemplate(template_file)
    email_service = EmailService(mailer, registration_template)
    email_service.send_simple_email(to_emails, context, subject)
    

import emails
from loguru import logger
from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING, Optional, Iterable, List
from datetime import timedelta

from emails.template import JinjaTemplate

from app.conf.config import settings, jwt_settings
from app.contrib.order.fetch import fetch_order_info
from app.utils.security import lazy_jwt_settings
from app.utils.templating import templates
from app.utils.translation import gettext_lazy as _, set_locale



def send_email(
        emails_to: List[str],
        subject_template: str = "",
        html_template: str = "",
        environment: Dict[str, Any] = None,
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    if environment is None:
        environment = {}
    message = emails.Message(
        subject=JinjaTemplate(subject_template, environment=templates.env),
        html=JinjaTemplate(html_template, environment=templates.env),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}

    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=emails_to, render=environment, smtp=smtp_options, set_mail_to=True)

    return response


def send_test_email(emails_to: List[str]) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    return send_email(
        emails_to=emails_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "emails": emails_to},
    )

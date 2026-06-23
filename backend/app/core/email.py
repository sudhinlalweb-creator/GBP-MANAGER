"""Transactional email delivery via Resend.

All public functions are synchronous (called from Celery tasks).
Templates are plain HTML strings — no template engine dependency.

To test locally without sending real email, set RESEND_API_KEY to any
non-empty string and check Resend's dashboard for delivery status.
"""

from __future__ import annotations

import logging

import resend

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _client() -> None:
    """Configure the Resend SDK with the API key from settings."""
    settings = get_settings()
    if not settings.resend_api_key:
        raise RuntimeError(
            "RESEND_API_KEY is not configured. "
            "Add it to your environment variables."
        )
    resend.api_key = settings.resend_api_key


def _from_address() -> str:
    return get_settings().email_from_address


def _frontend_url() -> str:
    return get_settings().frontend_url or "http://localhost:3000"


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def _base_template(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            background: #f5f1ec; margin: 0; padding: 40px 16px; color: #1a1916; }}
    .card {{ background: #ffffff; border-radius: 14px; max-width: 520px;
             margin: 0 auto; padding: 36px 32px; }}
    .logo {{ font-size: 18px; font-weight: 600; letter-spacing: -0.3px; margin-bottom: 28px; }}
    h1 {{ font-size: 20px; font-weight: 600; margin: 0 0 8px; letter-spacing: -0.3px; }}
    p {{ font-size: 14px; line-height: 1.6; color: #57534e; margin: 0 0 16px; }}
    .btn {{ display: inline-block; background: #1a1916; color: #ffffff;
            text-decoration: none; border-radius: 9px; padding: 11px 22px;
            font-size: 14px; font-weight: 500; margin: 8px 0 20px; }}
    .footer {{ font-size: 12px; color: #a8a29e; margin-top: 24px; }}
    .token {{ font-family: monospace; background: #f5f1ec; border-radius: 6px;
              padding: 10px 14px; font-size: 13px; color: #1a1916;
              word-break: break-all; margin: 8px 0 20px; display: block; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">GBP Manager</div>
    {body}
    <div class="footer">
      You're receiving this email because an action was taken on your GBP Manager account.
      If you didn't request this, you can safely ignore it.
    </div>
  </div>
</body>
</html>"""


def _password_reset_html(reset_link: str) -> str:
    body = f"""
    <h1>Reset your password</h1>
    <p>We received a request to reset the password for your GBP Manager account.
       Click the button below to choose a new password.</p>
    <a class="btn" href="{reset_link}">Reset password</a>
    <p>This link expires in <strong>1 hour</strong>. If you didn't request a password
       reset, no action is needed — your account is safe.</p>
    """
    return _base_template("Reset your GBP Manager password", body)


def _org_invite_html(org_name: str, accept_link: str) -> str:
    body = f"""
    <h1>You've been invited</h1>
    <p>You've been invited to join <strong>{org_name}</strong> on GBP Manager.
       Click below to accept the invitation and get started.</p>
    <a class="btn" href="{accept_link}">Accept invitation</a>
    <p>This invitation expires in <strong>7 days</strong>.</p>
    """
    return _base_template(f"Invitation to join {org_name}", body)


def _billing_alert_html(org_name: str, reason: str) -> str:
    reasons: dict[str, tuple[str, str]] = {
        "invoice.payment_failed": (
            "Payment failed",
            "We were unable to process your latest payment. Please update your billing "
            "details to avoid service interruption.",
        ),
    }
    subject, detail = reasons.get(reason, ("Billing alert", reason))
    body = f"""
    <h1>{subject}</h1>
    <p>{detail}</p>
    <a class="btn" href="{_frontend_url()}/settings?tab=billing">Update billing</a>
    """
    return _base_template(f"GBP Manager — {subject}", body)


# ---------------------------------------------------------------------------
# Public send functions (called by Celery tasks)
# ---------------------------------------------------------------------------

def send_password_reset(*, email: str, reset_token: str) -> None:
    """Send a password-reset email with a tokenised link."""
    _client()
    reset_link = f"{_frontend_url()}/reset-password?token={reset_token}"
    params: resend.Emails.SendParams = {
        "from": _from_address(),
        "to": [email],
        "subject": "Reset your GBP Manager password",
        "html": _password_reset_html(reset_link),
    }
    response = resend.Emails.send(params)
    logger.info("Password reset email sent to %s — id=%s", email, response.get("id"))


def send_org_invite(*, email: str, invite_token: str, org_name: str) -> None:
    """Send an organisation invite email with a tokenised accept link."""
    _client()
    accept_link = f"{_frontend_url()}/accept-invite?token={invite_token}"
    params: resend.Emails.SendParams = {
        "from": _from_address(),
        "to": [email],
        "subject": f"You've been invited to join {org_name} on GBP Manager",
        "html": _org_invite_html(org_name, accept_link),
    }
    response = resend.Emails.send(params)
    logger.info("Invite email sent to %s for org %s — id=%s", email, org_name, response.get("id"))


def send_billing_alert(*, org_id: str, org_name: str, reason: str) -> None:
    """Send a billing alert email to the organisation owner."""
    _client()
    params: resend.Emails.SendParams = {
        "from": _from_address(),
        "to": [org_id],  # caller must pass the owner email — see tasks.py
        "subject": "GBP Manager — Action required on your billing",
        "html": _billing_alert_html(org_name, reason),
    }
    response = resend.Emails.send(params)
    logger.info("Billing alert sent for org %s reason=%s — id=%s", org_id, reason, response.get("id"))

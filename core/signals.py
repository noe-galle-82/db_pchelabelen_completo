from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    """
    # Construir la URL de reset (esto debería apuntar a tu frontend)
    reset_password_url = f"http://localhost:5173/reset-password?token={reset_password_token.key}"
    
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': reset_password_url,
        'token': reset_password_token.key,
    }

    # Renderizar templates de email
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    # Crear el email
    msg = EmailMultiAlternatives(
        # título
        subject=getattr(settings, 'DJANGO_REST_PASSWORDRESET_EMAIL_SUBJECT', 'Password Reset'),
        # mensaje
        body=email_plaintext_message,
        # desde
        from_email=getattr(settings, 'DJANGO_REST_PASSWORDRESET_EMAIL_FROM', settings.DEFAULT_FROM_EMAIL),
        # para
        to=[reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
    
    print(f"📧 Email de recuperación enviado a: {reset_password_token.user.email}")
    print(f"🔑 Token: {reset_password_token.key}")
    print(f"🔗 URL: {reset_password_url}")
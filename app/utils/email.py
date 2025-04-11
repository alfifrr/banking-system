from flask_mail import Mail, Message
from flask import current_app

mail = Mail()


def send_activation_email(user, activation_url):
    msg = Message(
        subject='Activate your account',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    msg.body = f'''Hello {user.first_name},
    
    Please activate your account by clicking the following link:
    {activation_url}
    
    If you did not create this account, please ignore this email.
    '''
    mail.send(msg)

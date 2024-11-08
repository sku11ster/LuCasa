from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    
    def get_email_confirmation_url(self, request, emailconfirmation):
        return settings.FRONTEND_URL +  '/account/activate/{}'.format(emailconfirmation.key)
    
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        activate_url = f"{settings.FRONTEND_URL}/account/activate/{emailconfirmation.key}"
        
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "key": emailconfirmation.key,
        }
        
        if signup:
            email_template = "account/email/email_confirmation_message.html"
        else:
            email_template = "account/email/email_confirmation"
        
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)

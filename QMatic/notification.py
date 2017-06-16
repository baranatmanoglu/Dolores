#!/usr/bin/env python


from twilio.rest import Client
import qi

class Notification(object):
    account_sid = "AC6f499253df9e6c25d49f0b1f79f45855"
    auth_token = "6efeeb263f9c66d750cd6eda792e06e0"

    def __init__(self):
        self.service_name = self.__class__.__name__
        self.logger = qi.Logger(self.service_name)

    # public method for sending notification as an sms.
    def send_ticket(self, gsm_number, text):
        if gsm_number:

            self.logger.info("Sending text to: ", gsm_number)
            try:
                client = Client(self.account_sid, self.auth_token)
                message = client.messages.create(
                           to=str(gsm_number),
                           body=text,
                           from_="+16674018892")
                self.logger.info("Message sent:")
            except Exception,e:
                self.logger.info("Exception while sending sms {}".format(e))


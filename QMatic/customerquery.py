#!/usr/bin/env python
import requests
import qi


class CustomerQuery(object):
    customer_number = ''
    card_number = ''
    citizen_id = ''
    gsm_number = ''
    email_address = ''
    segment = ''
    name = ''
    last_name = ''

    _ENDPOINT_URL = "https://finie.herokuapp.com/api/pepper_customers/?"
    _username = "pocUser"
    _password = "MaxiFinie"

    def __init__(self):
        self.service_name = self.__class__.__name__
        self.logger = qi.Logger(self.service_name)

    #public method for getting customer info
    def query_customer(self, value1, type1):
        if type1 == "U":
            self.customer_number = value1
        elif type1 == "A":
            self.card_number = value1
        elif type1 == "I":
            self.citizen_id = value1
        #make the request here..

        url = self._ENDPOINT_URL + "inputNumber={}&inputType={}".format(value1,type1)
        r = requests.get(url, auth=(self._username, self._password))
        if r.status_code != 200:
            return
        r_json = r.json()
        self.logger.info(str(len(r_json)))
        if len(r_json) == 0:
            return
        if len(r_json[0]) == 0:
            return
        data = r_json[0][0]
        #end make request.

        self.customer_number = data["customer_number"]
        self.card_number = data["card_no"]
        self.citizen_id = data["citizen_id"]
        self.gsm_number = data["gsm_no"]
        self.email_address = data["email"]
        self.segment = data["segment"]
        self.name = data["name"]
        self.last_name = data["last_name"]
        return



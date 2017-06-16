#!/usr/bin/env python
import requests
import qi


class Qmatic(object):

    ticket_number = ""
    waiting_time = ""



    _ENDPOINT_URL = "https://finie.herokuapp.com/api/qmatic/?"
    _username = "pocUser"
    _password = "MaxiFinie"

    def __init__(self):
        self.service_name = self.__class__.__name__
        self.logger = qi.Logger(self.service_name)


    #public method for getting customer info
    def get_ticket(self, customer_no,segment, service_type):
        url = self._ENDPOINT_URL + "customerNumber={}&segment={}&serviceType={}".format(customer_no,segment, service_type)
        r = requests.get(url, auth=(self._username, self._password))
        if r.status_code != 200:
            return
        r_json = r.json()
        self.logger.info(str(len(r_json)))
        self.logger.info((r_json))
        if len(r_json) == 0:
            return

        data = r_json[0]
        #end make request.

        self.ticket_number = data["ticketNumber"]
        self.waiting_time = data["waitingTime"]

        return




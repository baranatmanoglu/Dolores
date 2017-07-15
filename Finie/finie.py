import requests
import json
import qi
import finie_settings
from time import gmtime, strftime

class FinieHelper(object):

    _customer_number = ""
    _access_token = ""
    _expire_duration = ""
    _scope = ""



    def __init__(self, customer_number):
        self._customer_number = customer_number
        self.service_name = self.__class__.__name__
        self.logger = qi.Logger(self.service_name)

    #Calls Finie API to get access token for current customer. First call this to get a token for current customer.
    def generate_token(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'client_id': finie_settings._client_id, 'client_secret': finie_settings._client_secret, 'grant_type' : finie_settings._grant_type, 'clinc_user_id': self._customer_number}
        try:
            r = requests.post(finie_settings._endpoint + "oauth/", data=data, timeout = finie_settings._timeout, headers = headers)
        except Exception,e:
            self.logger.info("Exception getting access token: {}".format(e))
            return False
        if r.status_code == requests.codes.ok:
            try:
                response = json.loads(r.text)
                self._access_token = response["access_token"]
                self._expire_duration = response["expires_in"] # This is ten hours, so no need to check/renew it on the actual call.
                self._scope = response["scope"]
                return True
            except Exception,e:
                self.logger.info("Exception parsing token response: {}".format(e))
                return False
        else:
            return False

    #Calls Finie API to make the actual query. After calling generate_token you can call this multiple times within 10 hours.
    #Gets string as query and returns json as response. {} if there is no successful response
    #Use response.visuals.formattedResponse to show the text on screen.
    # Use response.visuals.speakableResponse to make Pepper speak about it.
    #response.intent is the category of the response. The rest of response.visuals should be used according to the intent on web page.
    def query(self,query):
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self._access_token}
        data = self._build_query(query)
        try:
            self.logger.info("Request to Finie: {}".format(str(data)))
            r = requests.post(finie_settings._endpoint + "query/", data=data, timeout=finie_settings._timeout, headers = headers)
            self.logger.info("Response from Finie: {}".format(r.text))
        except Exception,e:
            self.logger.info("Exception getting access token: {}".format(e))
            return json.dumps({})

        if r.status_code == requests.codes.ok:
            try:
                response = json.loads(r.text)
                visuals = response["visuals"]
                intent = response["intent"]
                response = response["response"]
                pepper_response = {'visuals' : visuals, 'intent':intent, 'response':response}
                return json.dumps(pepper_response)
            except Exception, e:
                self.logger.info("Exception parsing query response: {}".format(e))
                return json.dumps({})
        else:
            return json.dumps({})


    #build the post data for query
    def _build_query(self, query):
        data = {'query': query,
                'lat': finie_settings._pepper_lat,
                'lon': finie_settings._pepper_long,
                'time_offset': int(strftime("%z", gmtime())) / 100 * 60,
                'classifier': '23class-stockprice-svm',
                'device': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'}
        return json.dumps(data)

#if __name__ == "__main__":
#    finie = Finie("100000001")
#    finie.generate_token()
#    json_resp = finie.query("What is the balance of my credit card?")
#    print json_resp
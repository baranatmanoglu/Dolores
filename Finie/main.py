#!/usr/bin/env python



import os
import sys
import qi
from finie import FinieHelper
import json
from customerquery import CustomerQuery

class Finie(object):
    subscriber_list = []
    in_action = False
    wentTeller = False





    def __init__(self, application):
        # get the session to use everywhere
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        self.logger = qi.Logger(self.service_name)
        self.logger.info("Initalizing: " + self.service_name)
        self.memory = self.session.service("ALMemory")
        self.create_signals()

        self.life = self.session.service("ALAutonomousLife")

        self.pm = self.session.service("ALPreferenceManager")
        
        self.redirect_pref_name = "feedback_app_id"
        self.tts = self.session.service("ALTextToSpeech")

        self.firstAnswer = True

        self.customerInfo = CustomerQuery()
        self.customer_json = ""
        try:
            self.customer_json = self.memory.getData("Global/CurrentCustomer")
            self.logger.info("Customer exists in memory: " + self.customerInfo.customer_number)
        except Exception,e:
            self.logger.info("Exception getting customer. Finie for anonymous user")
            self.on_exit()

        self.customerInfo.fromjson(self.customer_json)
        self.mapCustomerNumber()
        self.ticketData = ""
        try:
            self.ticketData = str(self.memory.getData("Global/QueueData"))
            self.logger.info("Get Ticket from Memory: {}".format(self.ticketData))
        except Exception,e:
            self.logger.info("No ticket requested")






    # Signal related methods starts

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")

        event_name = "Finie/StartSpeak"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_human_asked)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Finie/ExitApp"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_self_exit)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Finie/GoForTransaction"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_go_teller)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Finie/ReadyToGo"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_tablet_ready)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Finie/SpeakWithWhisper"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_speak_with_whisper)
        self.subscriber_list.append([event_subscriber, event_connection])


    @qi.nobind
    def disconnect_signals(self):
        self.logger.info("Deleting events...")
        for sub, i in self.subscriber_list:
            try:
                sub.signal.disconnect(i)
            except Exception, e:
                self.logger.info("Error unsubscribing: {}".format(e))
        self.logger.info("Unsubscribe done!")

    # Signal related methods ends

    # -------------------------------------

    # Event CallBacks Starts

    @qi.bind(methodName="on_tablet_ready", paramsType=(qi.String,), returnType=qi.Void)
    def on_tablet_ready(self, value):
        if self.ticketData != "":
            try:
                self.memory.raiseEvent("Finie/ShowTicketData",self.ticketData)
            except Exception,e:
                self.logger.info("exception {}".format(e))


    # Human Spoke

    @qi.bind(methodName="on_go_teller", paramsType=(qi.String,), returnType=qi.Void)
    def on_go_teller(self, value):
        self.wentTeller = True
        self.redirect_pref_name = "empty_app_id"
        self.tts.stopAll()
        number, waiting, service_type = self.ticketData.split("|")
        if service_type == "T":
            self.dialog.setConcept("tellerFinie", "English", ["You are next. Please proceed to teller booth {}".format(str(value))])
        else:
            self.dialog.setConcept("tellerFinie", "English",["You are next. Please proceed to customer representative booth {}".format(str(value))])
        self.dialog.gotoTag("goToTeller", "finie")



    @qi.bind(methodName="on_speak_with_whisper", paramsType=(qi.String,), returnType=qi.Void)
    def on_speak_with_whisper(self, value):
        self.memory.raiseEvent("Finie/TellResponse", self.spokenAnswer)

    @qi.bind(methodName="on_human_asked", paramsType=(qi.String,), returnType=qi.Void)
    def on_human_asked(self, value):
        if value:
            self.memory.raiseEvent("Finie/ShowLoading",1)
            self.logger.info("Get the input by event: {}".format(value))
            finieHelper = FinieHelper(self.customerInfo.customer_number)

            tokenGenerated = finieHelper.generate_token()
            if tokenGenerated == True:
                answer = finieHelper.query(value)
                answer_formatted = json.loads(answer)
                visuals = answer_formatted["visuals"]
                self.spokenAnswer =  visuals["speakableResponse"]
                intent = str(answer_formatted["intent"])
                strVisuals = str(json.dumps(visuals))
                self.logger.info("Visuals: {}".format(strVisuals))
                if not self.wentTeller:
                    offer = False
                    if intent == "history":
                        self.memory.raiseEvent("Finie/ShowPieChart",strVisuals)
                    if intent == "balance":
                        self.memory.raiseEvent("Finie/ShowBarChartForBalance", strVisuals)
                    if intent == "income":
                        self.memory.raiseEvent("Finie/ShowBarChartForIncome", strVisuals)
                    if intent == "spendadvice":
                        recommend = str(answer_formatted["response"]["accounts"]["recommendation"])
                        if recommend == "no":
                            self.dialog.setConcept("offerFinie", "English", ["Would you apply for an instant loan? That would help you with your spendings."])
                            self.memory.raiseEvent("Finie/ShowLineChartForAdvice", strVisuals)
                            offer = True
                    if not offer:
                        if self.firstAnswer and intent != "location":
                            self.memory.raiseEvent("Finie/PlayWhisper", self.spokenAnswer)
                            self.firstAnswer = False
                        else:
                            self.memory.raiseEvent("Finie/TellResponse", self.spokenAnswer)
                    else:
                        self.memory.raiseEvent("Finie/TellResponseWithOffer", self.spokenAnswer)

    @qi.nobind
    def on_self_exit(self, value):
        self.on_exit()




    # Event CallBacks Ends

    # -------------------------------------

    # Initiation methods for services Starts

    @qi.nobind
    def show_screen(self):
        folder = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
        self.logger.info("Loading tablet page for app: {}".format(folder))
        try:
            ts = self.session.service("ALTabletService")
            ts.loadApplication(folder)
            ts.showWebview()

            self.logger.info("Tablet loaded.")
        except Exception, e:
            self.logger.error("Error starting tablet page{}".format(e))


    @qi.nobind
    def hide_screen(self):
        self.logger.info("Stopping tablet")
        try:
            ts = self.session.service("ALTabletService")
            ts.hideWebview()
            self.logger.info("Tablet stopped.")
        except Exception, e:
            self.logger.error("Error hiding tablet page{}".format(e))


    @qi.nobind
    def start_dialog(self):
        self.logger.info("Loading dialog")
        self.dialog = self.session.service("ALDialog")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        topic_path = os.path.realpath(os.path.join(dir_path, "finie", "finie_enu.top"))
        self.logger.info("File is: {}".format(topic_path))
        try:
            self.loaded_topic = self.dialog.loadTopic(topic_path)
            self.dialog.activateTopic(self.loaded_topic)
            self.dialog.subscribe(self.service_name)
            self.logger.info("Dialog loaded!")
        except Exception, e:
            self.logger.info("Error while loading dialog: {}".format(e))
        self.dialog.gotoTag("finieStart", "finie")


    @qi.nobind
    def stop_dialog(self):
        self.logger.info("Unloading dialog")
        try:
            self.dialog = self.session.service("ALDialog")
            self.dialog.unsubscribe(self.service_name)
            self.dialog.deactivateTopic(self.loaded_topic)
            self.dialog.clearConcepts()
            self.dialog.unloadTopic(self.loaded_topic)
            self.logger.info("Dialog unloaded!")
        except Exception, e:
            self.logger.info("Error while unloading dialog: {}".format(e))

    # Initiation methods for services Ends

    # ------------------------------------------

    # App Start/End Methods Starts

    @qi.nobind
    def stop_app(self):
        # To be used if internal methods need to stop the service from inside.
        # external NAOqi scripts should use ALServiceManager.stopService if they need to stop it.
        self.logger.info("Stopping service...")
        self.cleanup()
        to_app = str(self.pm.getValue("global_variables", self.redirect_pref_name))
        self.logger.info("Switching to {}".format(to_app))
        self.life.switchFocus(to_app)

    @qi.nobind
    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")
        # @TODO: insert cleaning functions here
        self.disconnect_signals()
        self.stop_dialog()
        self.hide_screen()
        self.logger.info("Cleaned!")

    @qi.bind(methodName="on_exit", returnType=qi.Void)
    def on_exit(self):
        self.stop_app()

    @qi.nobind  # Starting the app  # @TODO: insert whatever the app should do to start
    def start_app(self):
        self.logger.info("Starting App.")
        self.show_screen()
        self.start_dialog()


    # App Start/End Methods Ends

    @qi.nobind
    def mapCustomerNumber(self):
        mappings = {'169858813': "100000001",
                    '155295662': "100000004",
                    '100000003':"100000003"}
        self.customerInfo.customer_number = mappings[self.customerInfo.customer_number]
        self.logger.info("Mapped customer number: {}".format(self.customerInfo.customer_number))


if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = Finie(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)

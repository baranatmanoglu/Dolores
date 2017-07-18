#!/usr/bin/env python



import os
import sys
import qi
import socket

from customerquery import CustomerQuery
from qmatic import Qmatic
import time

from notification import Notification


class QueueMatic(object):
    subscriber_list = []
    in_action = False




    message_text = "Your ticket number is: {}"

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
        self.customerInfo = CustomerQuery()
        self.ticketInfo = Qmatic()

        self.pm = self.session.service("ALPreferenceManager")
        self.pm.update()
        customer_json = ""
        try:
            customer_json = self.memory.getData("Global/CurrentCustomer")
            self.logger.info("Customer exists in memory: " + self.customerInfo.customer_number)
        except Exception,e:
            self.logger.info("QMatic for anonymous user")
        self.customerInfo.fromjson(customer_json)






    # Signal related methods starts

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")

        event_name = "QueueMatic/OptionSelected"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_option_selected)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "QueueMatic/ExitApp"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_self_exit)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "QueueMatic/CheckForCoffee"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_check_for_coffee)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "QueueMatic/CheckForAction"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_check_for_action)
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



    # Teller or Cust Rep. selected

    @qi.nobind
    def on_check_for_action(self, value):
        
        if not self.in_action:
            if value == "10":
                if self.customerInfo.name != "":
                    self.dialog.setConcept("introQ", "English", [
                        "{}, I could not hear you. Can you describe me the transaction you want to make in a few words?".format(
                            self.customerInfo.name)])
                else:
                    self.dialog.setConcept("introQ", "English", [
                        "I could not hear you. Can you describe me the transaction you want to make in a few words?"])
                self.memory.raiseEvent("QueueMatic/ReadyToGo",1)
            else:
                self.memory.raiseEvent("QueueMatic/NoAction",1)


    @qi.nobind
    def on_option_selected(self, value):
        try:

            self.in_action = True
            # Ticket obtained from Qmatic
            self.ticketInfo.get_ticket(self.customerInfo.customer_number, self.customerInfo.segment, value)
            ticketData = str(self.ticketInfo.ticket_number) + "|" + str(self.ticketInfo.waiting_time) + "|" + value
            self.memory.insertData("Global/QueueData", ticketData)
            self.logger.info("Ticket data inserted in memory: {}".format(ticketData))
            # Event raised for tablet to show the ticket number on the screen.
            if (value == "T"):
                ticket_ready = "Here is your ticket for your transaction with our teller."
            else:
                ticket_ready = "Here is your ticket for your transaction with our customer representative."

            if self.customerInfo.gsm_number != "":
                ticket_ready = self.customerInfo.name + ", " + ticket_ready + " I've also texted it to your mobile phone."


            self.dialog.setConcept("your_ticket_is_ready", "English", [ticket_ready])
            self.memory.raiseEvent("QueueMatic/ShowTicketNumber", self.ticketInfo.ticket_number)

            # If gsm is defined send sms
            if self.customerInfo.gsm_number != "":
                sendsms = Notification()
                sendsms.send_ticket(self.customerInfo.gsm_number,
                                    self.message_text.format(self.ticketInfo.ticket_number))
        except Exception, e:
            self.logger.info("Error while processing customer number: {}".format(e))

    @qi.nobind
    def on_self_exit(self, value):
        self.on_exit()


    @qi.nobind
    def on_check_for_coffee(self, value):
        time.sleep(2.0)
        self.logger.info("Waiting time: {}".format(self.ticketInfo.waiting_time))
        if self.ticketInfo.waiting_time >= 0:
            self.cleanup()
            to_app = str(self.pm.getValue("queuematic", "coffee_app"))
            self.logger.info("Switching to coffee app.")
            self.life.switchFocus(to_app)
        else:
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
        topic_path = os.path.realpath(os.path.join(dir_path, "qmatic", "qmatic_enu.top"))
        self.logger.info("File is: {}".format(topic_path))
        try:
            self.loaded_topic = self.dialog.loadTopic(topic_path)
            self.dialog.activateTopic(self.loaded_topic)
            self.dialog.subscribe(self.service_name)
            self.logger.info("Dialog loaded!")
        except Exception, e:
            self.logger.info("Error while loading dialog: {}".format(e))

        #initial dynamic concepts
        if self.customerInfo.name != "":
            self.dialog.setConcept("introQ", "English", [
                "{}, Can you describe me the transaction you want to make in a few words?".format(
                    self.customerInfo.name)])
        else:
            self.dialog.setConcept("introQ", "English", [
                "Can you describe me the transaction you want to make in a few words?"])

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
        to_app = str(self.pm.getValue("global_variables", "main_app_id"))
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
        self.memory.raiseEvent("QueueMatic/ShowNumPad", "1")


    # App Start/End Methods Ends




if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = QueueMatic(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)

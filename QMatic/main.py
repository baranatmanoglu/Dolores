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

        self.customer_number = "169858813"#self.memory.getData("Global/CurrentCustomerNumber")
        self.logger.info("Customer Number exists in memory: " + self.customer_number)

        if self.customer_number != "":
            self.customerInfo.query_customer(self.customer_number, "U")



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
                    self.dialog.setConcept("intro", "English", [
                        "{}, I could not hear you. Can you describe me the transaction you want to make in a few words?".format(
                            self.customerInfo.name)])
                else:
                    self.dialog.setConcept("intro", "English", [
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
        if self.ticketInfo.waiting_time > 8:
            self.cleanup()
            self.life.switchFocus("coffeemaker-6aac2e/coffeemaker")
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
            self.dialog.setConcept("intro", "English", [
                "{}, Can you describe me the transaction you want to make in a few words?".format(
                    self.customerInfo.name)])
        else:
            self.dialog.setConcept("intro", "English", [
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
        self.application.stop()

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

    # ------------------------------------------

    # Smart Plug Communication Starts

    @qi.nobind
    def run_tcp_command(self, cmd):
        try:
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.connect(("10.44.110.161", 9999))
            sock_tcp.send(self.encrypt(cmd))
            data = sock_tcp.recv(2048)
            sock_tcp.close()
            self.logger.info(self.decrypt(data[4:]))
            return True

        except Exception, e:
            self.logger.info("Error while sending message to plug: {}".format(e))
            return False

    @qi.nobind
    def encrypt(self, string):
        key = 171
        result = "\0\0\0\0"
        for i in string:
            a = key ^ ord(i)
            key = a
            result += chr(a)
        return result



    @qi.nobind
    def decrypt(self, string):
        key = 171
        result = ""
        for i in string:
            a = key ^ ord(i)
            key = ord(i)
            result += chr(a)
        return result

    # Smart Plug Communication Ends


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

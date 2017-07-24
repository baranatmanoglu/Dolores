#!/usr/bin/env python



import os
import sys
import qi

from datetime import datetime
from customerquery import CustomerQuery
from kairos_face import enroll

class Numpad(object):
    subscriber_list = []
    found = False
    trialCount = 1
    




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



        self.preferences = self.session.service("ALPreferenceManager")

        self.connect_to_preferences()



    @qi.nobind
    def connect_to_preferences(self):
        # connects to cloud preferences library and gets the initial prefs
        try:

            self.gallery_name = self.preferences.getValue('my_friend', "gallery_name")
            self.folder_path = self.preferences.getValue('my_friend', "folder_path")
            self.logger.info(self.folder_path)
            self.threshold = float(str(self.preferences.getValue('my_friend', "threshold")))

            self.logger.info(self.threshold)
            self.record_folder = self.preferences.getValue('my_friend', "record_folder")
            self.file_name = self.preferences.getValue('my_friend', "file_name")

        except Exception, e:
            self.logger.info("failed to get preferences".format(e))
        self.logger.info("Successfully connected to preferences system")

    # Signal related methods starts

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")

        event_name = "Numpad/NumberEntered"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_number_entered)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Numpad/ExitApp"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_self_exit)
        self.subscriber_list.append([event_subscriber, event_connection])


        event_name = "Numpad/CheckForAction"
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



    @qi.nobind
    def on_check_for_action(self, value):
        self.logger.info(str(value))
        if not self.found:
            if value == "reminder":
                self.memory.raiseEvent("Numpad/Reminder",1)
            elif value == "endit":
                self.memory.raiseEvent("Numpad/NoAction",1)




    @qi.nobind
    def on_number_entered(self, value):
        self.memory.raiseEvent("Numpad/ShowLoading",1)
        try:
            self.logger.info(str(value))
            self.found = False
            if len(value) == 11:
                self.found = self.customerInfo.query_customer(value, "I")
            else:
                self.found = self.customerInfo.query_customer(value, "U")
            if self.found:
                self.memory.insertData("Global/CurrentCustomer", self.customerInfo.jsonify())
                self.register_face(self.customerInfo.customer_number, self.file_name)
                self.cleanup()
                next_app = str(self.memory.getData("Global/RedirectingApp"))
                try:
                    self.logger.info("Switching to {}".format(next_app))
                    self.life.switchFocus(next_app)
                except Exception, e:
                    self.logger.info("Error while switching to next app: {} {}".format(next_app, e))
            else:
                self.memory.raiseEvent("Numpad/HideLoading", 1)
                self.memory.raiseEvent("Numpad/NoCustomer", self.trialCount)
                self.trialCount += 1

        except Exception, e:
            self.logger.info("Error while setting customer number: {}".format(e))




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
        topic_path = os.path.realpath(os.path.join(dir_path, "numpad", "numpad_enu.top"))
        self.logger.info("File is: {}".format(topic_path))
        try:
            self.loaded_topic = self.dialog.loadTopic(topic_path)
            self.dialog.activateTopic(self.loaded_topic)
            self.dialog.subscribe(self.service_name)
            self.logger.info("Dialog loaded!")
        except Exception, e:
            self.logger.info("Error while loading dialog: {}".format(e))

       

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
        to_app = str(self.preferences.getValue("global_variables", "main_app_id"))
        self.life.switchFocus(to_app)

    @qi.nobind
    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")
        # @TODO: insert cleaning functions here
        self.hide_screen()
        self.stop_dialog()
        self.disconnect_signals()
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


    # kairos started


    @qi.bind(methodName="registerFace", paramsType=(qi.String, qi.String,), returnType=qi.Bool)
    def register_face(self, customer_id, picture_name):
        try:
            file_path = self.get_picture_path(picture_name)
            self.logger.info("Photo send with file name: {} at {}".format(file_path, str(datetime.now())))
            response = enroll.enroll_face(subject_id=customer_id, gallery_name=self.gallery_name, file=file_path)
            self.logger.info(response)
            return True
        except Exception, e:
            self.logger.error(e)
            return False

    @qi.nobind
    def get_picture_path(self, picture_name):
        image_path = self.folder_path + picture_name
        return image_path

    # kairos ended


if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = Numpad(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)

#!/usr/bin/env python



import os
import sys
import qi
import json
from customerquery import CustomerQuery

class Feedback(object):
    subscriber_list = []
    in_action = False





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


        self.audio = self.session.service('ALAudioDevice')
        self.audioFilePath = '/home/nao/recordings/audio/'

        self.customerInfo = CustomerQuery()
        customer_json = ""
        try:
            customer_json = self.memory.getData("Global/CurrentCustomer")
            self.logger.info("Customer exists in memory: " + self.customerInfo.customer_number)
        except Exception, e:
            self.logger.info("Feedback for anonymous user")
        self.customerInfo.fromjson(customer_json)


    # Signal related methods starts

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")

        event_name = "Feedback/SurveyClicked"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_survey_clicked)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Feedback/ProcessRecording"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_process_recording)
        self.subscriber_list.append([event_subscriber, event_connection])


        event_name = "Feedback/CheckForAction"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_check_for_action)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Feedback/ExitApp"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_self_exit)
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

    @qi.bind(methodName="on_check_for_action", paramsType=(qi.String,), returnType=qi.Void)
    def on_check_for_action(self, value):
        self.logger.info(str(value))
        if not self.in_action:
            if value == "reminder":
                self.memory.raiseEvent("Feedback/Reminder", 1)
            elif value == "endit":
                self.memory.raiseEvent("Feedback/NoAction", 1)

    @qi.bind(methodName="on_survey_clicked", paramsType=(qi.String,), returnType=qi.Void)
    def on_survey_clicked(self, value):
        self.logger.info(str(value))
        self.in_action = True

    @qi.bind(methodName="on_process_recording", paramsType=(qi.String,), returnType=qi.Void)
    def on_process_recording(self, value):
        self.logger.info(str(value))
        if str(value) == "S":
            self.start_record()
        else:
            self.stop_record()
            self.memory.raiseEvent("Feedback/VoiceRecorded",1)



        
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
        topic_path = os.path.realpath(os.path.join(dir_path, "feedback", "feedback_enu.top"))
        self.logger.info("File is: {}".format(topic_path))
        try:
            self.loaded_topic = self.dialog.loadTopic(topic_path)
            self.dialog.activateTopic(self.loaded_topic)
            self.dialog.subscribe(self.service_name)
            self.logger.info("Dialog loaded!")
            self.dialog.gotoTag("feedbackStart","feedback")
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
        to_app = str(self.pm.getValue("global_variables", "empty_app_id"))
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



    @qi.bind(methodName="start_record", paramsType=(qi.String,), returnType=qi.Void)
    def start_record(self):

        # folder_path='/home/nao/recordings/audio/'
        # file_name=str(uuid.uuid4().hex)+'.ogg'
        # audioName=folder_path+file_name
        try:
            filename = "feedback"
            self.logger.info("Audio record has been started file path:".format(self.audioFilePath))
            if self.customerInfo.customer_number != "":
                filename = self.customerInfo.customer_number
            fullpath = self.audioFilePath + filename + ".wav"
            self.logger.info("Audio record has been started file path: {}".format(fullpath))
            self.audio.startMicrophonesRecording(fullpath)
        except Exception,e:
            self.logger.info("Exception while starting recording; {}".format(e))

    @qi.bind(methodName="stop_record", paramsType=(qi.String,), returnType=qi.Void)
    def stop_record(self):
        self.audio.stopMicrophonesRecording()



if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = Feedback(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)

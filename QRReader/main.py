#!/usr/bin/env python

import sys
import qi
import os
import json
import time

from datetime import datetime
from customerquery import CustomerQuery
from kairos_face import enroll
from threading import Lock



class QRReader(object):
    subscriber_list = []
    loaded_topic = ""
    barcode_detected = False

    def __init__(self, application):
        # Get session
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        # Get logger -> stored in: /var/log/naoqi/servicemanager/{application id}.{service name}
        self.logger = qi.Logger(self.service_name)
        # Do initialization before the service is registered to NAOqi
        self.logger.info("Initializing...")

        # Autonomous Life
        self.life = self.session.service("ALAutonomousLife")
        self.customerInfo = CustomerQuery()

        # Preferences
        self.preferences = self.session.service("ALPreferenceManager")
        self.logger.info("Initializing - ALPreferenceManager")

        # Memory
        self.memory = self.session.service("ALMemory")
        self.logger.info("Initializing - ALMemory")

        self.lock = Lock()

        self.dialog = self.session.service("ALDialog")

        # Barcode Reader
        self.barcode_reader = self.session.service("ALBarcodeReader")
        self.logger.info("Initializing - ALBarcodeReader")

        # Create Signals
        self.create_signals()

        self.logger.info("Initialized!")


    @qi.nobind
    def connect_to_preferences(self):
        # connects to cloud preferences library and gets the initial prefs
        try:
            self.gallery_name = self.preferences.getValue('my_friend', "gallery_name")
            self.folder_path = self.preferences.getValue('my_friend', "folder_path")
            self.logger.info(self.folder_path)
            self.threshold = float(str(self.preferences.getValue('my_friend', "threshold")))
            self.record_folder = self.preferences.getValue('my_friend', "record_folder")
            self.photo_count = int(self.preferences.getValue('my_friend', "photo_count"))
            self.resolution = int(self.preferences.getValue('my_friend', "resolution"))
            self.camera_id = int(self.preferences.getValue('my_friend', "camera_id"))
            self.picture_format = self.preferences.getValue('my_friend', "picture_format")
            self.file_name = self.preferences.getValue('my_friend', "file_name")
            self.logger.info("File name: " + self.file_name)
            self.logger.info("Successfully connected to preferences system")
        except Exception, e:
            self.logger.info(e)

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")

        event_name = "BarcodeReader/BarcodeDetected"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_barcode_detected)
        self.subscriber_list.append([event_subscriber, event_connection])
        self.logger.info("Subscribed to event: " + event_name)

        event_name = "QRReader/ExitApp"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_self_exit)
        self.subscriber_list.append([event_subscriber, event_connection])
        self.logger.info("Subscribed to event: " + event_name)

        event_name = "QRReader/StartTimer"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_user_ready)
        self.subscriber_list.append([event_subscriber, event_connection])
        self.logger.info("Subscribed to event: " + event_name)

        self.logger.info("Subscribed to all events.")

    @qi.nobind
    def disconnect_signals(self):
        self.logger.info("Deleting events...")
        for sub, i in self.subscriber_list:
            try:
                sub.signal.disconnect(i)
            except Exception, e:
                self.logger.info("Error unsubscribing: {}".format(e))
        self.logger.info("Unsubscribe done!")

    # Signal related methods end

    # ---------------------------

    # Event CallBacks Start

    @qi.nobind
    def on_user_ready(self, value):
        seconds = 0
        self.logger.info("User Ready")
        while not self.barcode_detected:
            if seconds == 10:
                self.logger.info("Raised event: QRReader/Reminder")
                self.memory.raiseEvent("QRReader/Reminder", 1)
            if seconds == 15:
                self.logger.info("Raised event: QRReader/NoAction")
                self.barcode_detected = True
                self.memory.raiseEvent("QRReader/StopVideo", 1)
            time.sleep(1)
            seconds += 1


    @qi.nobind
    def on_barcode_detected(self, value):
        self.lock.acquire()
        if not self.barcode_detected:
            self.barcode_detected = True
            self.lock.release()
            self.logger.info("Barcode detected...")
            try:
                encoded_info = str(value[0][0]).replace(" ", "")
                self.logger.info("Information in QR: " + encoded_info)
                found = self.customerInfo.query_customer(value1=encoded_info, type1="U")

                if found:
                    self.memory.insertData("Global/CurrentCustomer", self.customerInfo.jsonify())
                    self.register_face(self.customerInfo.customer_number, self.file_name)
                    # Redirect to next app
                    self.cleanup()
                    next_app = str(self.memory.getData("Global/RedirectingApp"))
                    try:
                        self.logger.info("Switching to {}".format(next_app))
                        self.life.switchFocus(next_app)
                    except Exception, e:
                        self.logger.info("Error while switching to next app: {} {}".format(next_app, e))
                else:
                    self.memory.raiseEvent("QRReader/NoCustomer", 1)
            except Exception, e:
                self.logger.info("Error while querying customer: {}".format(e))
        else:
            self.lock.release()



    @qi.nobind
    def on_self_exit(self, value):
        self.stop_app()

    # Event CallBacks End

    # -------------------

    # Initiation methods for services start

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
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        topic_path = os.path.realpath(os.path.join(dir_path, "barcode_detected", "barcode_detected_enu.top"))
        self.logger.info("File is: {}".format(topic_path))
        try:
            self.loaded_topic = self.dialog.loadTopic(topic_path)
            self.dialog.activateTopic(self.loaded_topic)
            self.dialog.subscribe(self.service_name)
            self.logger.info("Dialog loaded!")
        except Exception, e:
            self.logger.info("Error while loading dialog: {}".format(e))
        self.dialog.gotoTag("startQR", "barcode_detected")

    @qi.nobind
    def stop_dialog(self):
        self.logger.info("Unloading dialog")
        try:
            
            self.dialog.unsubscribe(self.service_name)
            self.dialog.deactivateTopic(self.loaded_topic)
            self.dialog.unloadTopic(self.loaded_topic)
            self.logger.info("Dialog unloaded!")
        except Exception, e:
            self.logger.info("Error while unloading dialog: {}".format(e))

    # Initiation methods for services end

    # -----------------------------------

    # App Start/End Methods start

    @qi.nobind
    def start_app(self):
        # do something when the service starts
        self.logger.info("Starting app...")
        self.show_screen()
        self.start_dialog()
        self.connect_to_preferences()
        self.logger.info("Started!")

    @qi.nobind
    def stop_app(self):
        self.logger.info("Stopping service...")
        self.cleanup()
        to_app = str(self.preferences.getValue("global_variables", "main_app_id"))
        self.life.switchFocus(to_app)

    @qi.nobind
    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")

        self.hide_screen()
        self.stop_dialog()
        self.disconnect_signals()
        self.logger.info("Cleaned!")


    # App Start / End methods end

    # ---------------------------

    # Kairos Starts
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


    # Kairos ends

if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = QRReader(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)


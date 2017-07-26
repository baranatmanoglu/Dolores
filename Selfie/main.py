#!/usr/bin/env python

import sys
import qi
import os
import socket


class Selfie(object):
    subscriber_list = []
    loaded_topic = ""

    def __init__(self, application):
        # Get session
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        # Get logger -> stored in: /var/log/naoqi/servicemanager/{application id}.{service name}
        self.logger = qi.Logger(self.service_name)
        # Do initialization before the service is registered to NAOqi
        self.logger.info("Initializing...")

        # Dialog
        self.dialog = self.session.service("ALDialog")
        self.logger.info("Initializing - ALDialog...")

        # Autonomous Life
        self.life = self.session.service("ALAutonomousLife")
        self.logger.info("Initializing - ALAutonomousLife...")

        # Memory
        self.memory = self.session.service("ALMemory")
        self.logger.info("Initializing - ALMemory...")
        
        self.posture = self.session.service("ALRobotPosture")

        # Preferences
        self.preferences = self.session.service("ALPreferenceManager")
        self.logger.info("Initializing - ALPreferenceManager...")
        self.preferences.update()
        self.connect_to_preferences()

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
            self.cm_ip = str(self.preferences.getValue('cm', 'cm_ip'))
            self.cm_port = int(self.preferences.getValue('cm', 'cm_port'))
            self.record_folder = self.preferences.getValue('my_friend', "record_folder")
            self.photo_count = int(self.preferences.getValue('my_friend', "photo_count"))
            self.resolution = int(self.preferences.getValue('my_friend', "resolution"))
            self.camera_id = int(self.preferences.getValue('my_friend', "camera_id"))
            self.picture_format = self.preferences.getValue('my_friend', "picture_format")
            self.file_name = self.preferences.getValue('my_friend', "file_name")
        except Exception, e:
            self.logger.info("failed to get preferences".format(e))
        self.logger.info("Successfully connected to preferences system")

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")
        # TODO: Create events
        event_name = "Selfie/Animation"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_start_animation)
        self.subscriber_list.append([event_subscriber, event_connection])
        self.logger.info("Subscribed to event: " + event_name)

        event_name = "Selfie/EndAnimation"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_end_animation)
        self.subscriber_list.append([event_subscriber, event_connection])
        self.logger.info("Subscribed to event: " + event_name)

        event_name = "Selfie/ExitApp"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_self_exit)
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
    def on_start_animation(self, value):
        self.logger.info("Event Raised - Selfie/Animation")
        #self.stop_dialog()
        #self.logger.info("Animation Started - Dialog Stopped! ")
        self.lights_on()
        self.life.setAutonomousAbilityEnabled("BasicAwareness", False)
        self.logger.info("Animation Started - BasicAwareness off! ")

    @qi.nobind
    def on_end_animation(self, value):
        self.logger.info("Event Raised - Selfie/EndAnimation")
        
        #self.start_dialog()
        self.logger.info("Animation Ended - Dialog Started! ")
        self.dialog.gotoTag("joke", "selfie")

        self.life.setAutonomousAbilityEnabled("BasicAwareness", True)
        self.logger.info("Animation Ended - BasicAwareness on!")


    @qi.nobind
    def on_self_exit(self, value):
        self.logger.info("Event Raised - ExitApp")
        self.lights_off()
        self.on_exit()

    @qi.nobind
    def lights_on(self):
        self.logger.info("Turning lights on...")
        cmd = '{"system":{"set_relay_state":{"state":1}}}'
        self.run_tcp_command(cmd)

    @qi.nobind
    def lights_off(self):
        self.logger.info("Turning lights off...")
        cmd = '{"system":{"set_relay_state":{"state":0}}}'
        self.run_tcp_command(cmd)

    # Event CallBacks End

    # ---------------------------

    # Smart Plug Connection Starts

    @qi.nobind
    def run_tcp_command(self, cmd):
        try:
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.info("cm_ip: " + self.cm_ip)
            sock_tcp.connect((self.cm_ip, self.cm_port))
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

    # -------------------------------------

    # Initiation methods for services start
    @qi.nobind
    def on_exit(self):
        self.stop_app()

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
        topic_path = os.path.realpath(os.path.join(dir_path, "selfie", "selfie_enu.top"))
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
            self.dialog.unsubscribe(self.service_name)
            self.dialog.deactivateTopic(self.loaded_topic)
            self.dialog.clearConcepts()
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
        self.dialog.gotoTag("begin", "selfie")
        self.logger.info("Started!")

    @qi.nobind
    def stop_app(self):
        # To be used if internal methods need to stop the service from inside.
        # external NAOqi scripts should use ALServiceManager.stopService if they need to stop it.
        self.logger.info("Stopping service...")
        self.cleanup()

        to_app = str(self.preferences.getValue("global_variables", "main_app_id"))
        self.logger.info("Switching to {}".format(to_app))
        self.life.switchFocus(to_app)

    @qi.nobind
    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")

        self.disconnect_signals()
        self.stop_dialog()
        self.hide_screen()

        self.logger.info("Cleaned!")
        try:
            self.audio.stopMicrophonesRecording()
        except Exception, e:
            self.logger.info("Microphone already closed")



if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = Selfie(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)
#!/usr/bin/env python

import sys
import qi
import os


class GuideApp(object):
    subscriber_list = []
    loaded_topic = ""
    next_app = ""
    
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
        self.logger.info("Initializing - ALDialog...")
        self.dialog = self.session.service("ALDialog")
        

        # Preference Manager
        self.logger.info("Initializing - ALPreferenceManager...")
        self.preferences = self.session.service("ALPreferenceManager")

        # Memory
        self.logger.info("Initializing - ALMemory...")
        self.memory = self.session.service("ALMemory")

        # Autonomous Life
        self.logger.info("Initializing - ALAutonomousLife...")
        self.life = self.session.service("ALAutonomousLife")

        self.create_signals()
        self.connect_to_preferences()

        self.logger.info("Initialized!")

    # Preferences

    @qi.nobind
    def connect_to_preferences(self):
        # connects to cloud preferences library and gets the initial prefs
        self.logger.info("Connecting to preferences...")
        try:
            self.next_app = str(self.preferences.getValue("global_variables", "main_app_id"))
            self.logger.info("Preferences successfully retrieved!")
        except Exception, e:
            self.logger.info("Error while connecting to preferences: {} ".format(e))

    # Event - signal related methods start

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")

        event_name = "GuideApp/ExitApp"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_self_exit)
        self.subscriber_list.append([event_subscriber, event_connection])
        self.logger.info("Subscribed to event: " + event_name)

        self.logger.info("Subscribed to all event!")

    @qi.nobind
    def disconnect_signals(self):
        self.logger.info("Deleting events...")
        for sub, i in self.subscriber_list:
            try:
                sub.signal.disconnect(i)
            except Exception, e:
                self.logger.info("Error unsubscribing: {}".format(e))
        self.logger.info("Unsubscribe done!")

    # Event - signal related methods end

    # Event Call Back Methods start

    @qi.nobind
    def on_self_exit(self, value):
        self.logger.info("Exiting app")
        self.cleanup()

        try:
            self.logger.info("Switching to {}".format(self.next_app))
            self.life.switchFocus(self.next_app)
        except Exception, e:
            self.logger.info("Error while switching apps: {} ".format(e))

    # Event Call Back Methods end

    # App Start/End methods start

    @qi.nobind
    def start_app(self):
        # do something when the service starts
        self.logger.info("Starting app...")

        self.show_screen()
        self.start_dialog()

        self.logger.info("App started!")

    @qi.nobind
    def stop_app(self):
        # To be used if internal methods need to stop the service from inside.
        # external NAOqi scripts should use ALServiceManager.stopService if they need to stop it.
        self.logger.info("Stopping service...")
        self.application.stop()
        self.logger.info("Stopped!")

    @qi.nobind
    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")

        self.disconnect_signals()
        self.stop_dialog()
        self.hide_screen()

        self.logger.info("Cleaned!")

    # Dialog Start/Stop

    @qi.nobind
    def start_dialog(self):
        self.logger.info("Loading dialog")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        topic_path = os.path.realpath(os.path.join(dir_path, "guidedialog", "guidedialog_enu.top"))
        self.logger.info("File is: {}".format(topic_path))
        try:
            self.loaded_topic = self.dialog.loadTopic(topic_path)
            self.dialog.activateTopic(self.loaded_topic)
            self.dialog.subscribe(self.service_name)
            self.dialog.addBlockingEvent("GuideApp/ExitApp")
            self.logger.info("Dialog loaded!")
        except Exception, e:
            self.logger.info("Error while loading dialog: {}".format(e))
        self.dialog.gotoTag("start", "guidedialog")

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

    # Screen Show/Hide

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


if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = GuideApp(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)

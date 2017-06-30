#!/usr/bin/env python



import os
import sys
import qi
import json

class AuthenticationLauncher(object):
    subscriber_list = []






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
        self.pm.update()

        self.amoves = self.session.service("ALAutonomousMoves")
        self.bawareness = self.session.service("ALBasicAwareness")
        self.aspeech = self.session.service("ALAnimatedSpeech")
        self.posture = self.session.service("ALRobotPosture")


    # Signal related methods starts

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")

        event_name = "Authentication/GoNFC"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_go_nfc)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/GoQR"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_go_qr)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/GoListener"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_go_listener)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/GoKeyboard"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_go_keyboard)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/EnableBasics"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.enable_after_first_animation)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/CheckForAction"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_check_for_action)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/ExitApp"
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
                self.memory.raiseEvent("Authentication/Reminder", 1)
            elif value == "endit":
                self.memory.raiseEvent("Authentication/NoAction", 1)

    @qi.bind(methodName="on_go_nfc", paramsType=(qi.String,), returnType=qi.Void)
    def on_go_nfc(self, value):
        self.logger.info("NFC selected.")
        to_app = str(self.pm.getValue("authentication_launcher", "nfc_app"))
        self.logger.info(to_app)
        self.cleanup()
        self.life.switchFocus(to_app)

    @qi.bind(methodName="on_go_qr", paramsType=(qi.String,), returnType=qi.Void)
    def on_go_qr(self, value):
        self.logger.info("QR selected.")
        to_app = str(self.pm.getValue("authentication_launcher", "qr_app"))
        self.logger.info(to_app)
        self.cleanup()
        self.life.switchFocus(to_app)

    @qi.bind(methodName="on_go_listener", paramsType=(qi.String,), returnType=qi.Void)
    def on_go_listener(self, value):
        self.logger.info("Listener selected.")
        to_app = str(self.pm.getValue("authentication_launcher", "listener_app"))
        self.logger.info(to_app)
        self.cleanup()
        self.life.switchFocus(to_app)

    @qi.bind(methodName="on_go_keyboard", paramsType=(qi.String,), returnType=qi.Void)
    def on_go_keyboard(self, value):
        self.logger.info("Keyboard selected.")
        to_app = str(self.pm.getValue("authentication_launcher", "keyboard_app"))
        self.logger.info(to_app)
        self.cleanup()
        self.life.switchFocus(to_app)

    @qi.nobind  # Disables the awareness and animation language for intro part
    def enable_after_first_animation(self, value):
        self.posture.goToPosture("Stand", 0.8)
        try:
            self.amoves.setBackgroundStrategy("backToNeutral")
        except Exception, e:
            self.logger.info("Exception while disabling autonomus moves: {}".format(e))

        try:
            self.bawareness.startAwareness()
        except Exception, e:
            self.logger.info("Exception while disabling basic awareness: {}".format(e))

        try:
            self.aspeech.setBodyLanguageModeFromStr("contextual")
        except Exception, e:
            self.logger.info("Exception while disabling animated speech: {}".format(e))

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
        topic_path = os.path.realpath(os.path.join(dir_path, "authentication", "authentication_enu.top"))
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
        self.disable_for_first_animation()
        self.show_screen()
        self.start_dialog()

    @qi.nobind #Disables the awareness and animation language for intro part
    def disable_for_first_animation(self):
        try:
            self.amoves.setBackgroundStrategy("none")
        except Exception, e:
            self.logger.info("Exception while disabling autonomus moves: {}".format(e))
        try:
            self.bawareness.stopAwareness()
        except Exception, e:
            self.logger.info("Exception while disabling basic awareness: {}".format(e))
        try:
            self.aspeech.setBodyLanguageModeFromStr("disabled")
        except Exception,e:
            self.logger.info("Exception while disabling animated speech: {}".format(e))
        self.posture.goToPosture("Stand", 0.8)


    # App Start/End Methods Ends




if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = AuthenticationLauncher(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)

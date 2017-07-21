#!/usr/bin/env python



import os
import sys
import qi


class PairGame(object):
    subscriber_list = []
    in_action = False
    audio_path = ""




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
        self.audio = self.session.service("ALAudioPlayer")

        self.audio_path = os.path.dirname(os.path.realpath(__file__)) + "/sounds/"

        self.preferences = self.session.service("ALPreferenceManager")

        self.show_screen()
        self.animal = "elephant"

    # Signal related methods starts

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")

        event_name = "PairGame/PairFound"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_pair_found)
        self.subscriber_list.append([event_subscriber, event_connection])


        event_name = "PairGame/PairNotFound"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_pair_not_found)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "PairGame/GameFinished"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_game_finished)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "PairGame/AbortGame"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_self_exit)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "PairGame/AnimalTrivia"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_animal_trivia)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "PairGame/PlayAnimalSound"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_play_sound)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "PairGame/CheckForAction"
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
    def on_play_sound(self, value):
        self.logger.info("Playing sound for {}".format(self.animal))
        try:
            
            self.audio.playFile(self.audio_path + "" + self.animal + ".wav", 1.0, 0.0)
        except Exception,e:
            self.logger.info("Exception while playing sound: {}".format(e))
   
    @qi.nobind
    def on_pair_found(self,value):
        self.logger.info("New pair found {}".format(str(value)))
        ratio,self.animal = str(value).split(";")
        if(ratio == "G"):
            self.dialog.gotoTag("say_good", "pair_game")
        else:
            self.dialog.gotoTag("say_normal", "pair_game")

    @qi.nobind
    def on_animal_trivia(self, value):
        self.logger.info("Animal: {}".format(self.animal))
        self.dialog.gotoTag(self.animal, "pair_game")


    @qi.nobind
    def on_pair_not_found(self, value):
        self.logger.info("No pair found..")
        self.dialog.gotoTag("say_no_pair", "pair_game")

    @qi.nobind
    def on_game_finished(self, value):
        self.logger.info("Game finished")
        self.dialog.gotoTag("game_end", "pair_game")
        
    @qi.nobind
    def on_check_for_action(self, value):
        self.logger.info(str(value))
        if value == "reminder":
            self.memory.raiseEvent("PairGame/Reminder",1)
        elif value == "endit":
            self.memory.raiseEvent("PairGame/NoAction",1)




    

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
        topic_path = os.path.realpath(os.path.join(dir_path, "pair_game", "pair_game_enu.top"))
        self.logger.info("File is: {}".format(topic_path))
        try:
            self.loaded_topic = self.dialog.loadTopic(topic_path)
            self.dialog.activateTopic(self.loaded_topic)
            self.dialog.subscribe(self.service_name)
            self.logger.info("Dialog loaded!")
        except Exception, e:
            self.logger.info("Error while loading dialog: {}".format(e))
        self.dialog.gotoTag("game_start","pair_game")
       

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

        self.start_dialog()


    # App Start/End Methods Ends


   


if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = PairGame(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)

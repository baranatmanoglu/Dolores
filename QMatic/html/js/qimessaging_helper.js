/**

just to make things easier:
instead of using QiSession( function(session) { session.xxxx ... }, function(error) { error catching stuff }, address)
we make a promise for the session, that becomes available when session is connected
then some helpers:
 * session.service to get a service : session.service("ALTextToSpeech").then( function(tts) { tts.say();});
 * session.raiseEvent("myevent", "the event value");
 * session.subscribeToEvent("myevent", callbackFunction);

Plus debugging helper:
 * in your browser, open the page from your computer with ?robot=192.168.123.123 to debug. This will connect to the remote naoqi.

/!\ This is only an example. There is NO support and nothing official about it: you don't have to use it!

**/



session = (function(self, $) {

    self = new Promise(function(resolve, reject) {
        // Private helper functions
        function _getRobotIp() {
            var regex = new RegExp("[\\?&]robot=([^&#]*)");
            var results = regex.exec(location.search);
            return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " ").replace("/", ""));
        }
        var robotIp = _getRobotIp();
        // Session promise
        var robotAddress = "";
        var qimAddress = null;
        if (robotIp) {
            // Special case: we're doing remote debugging on a robot.
            robotAddress = "http://" + robotIp;
            qimAddress = robotIp + ":80";
        }
        $.getScript(robotAddress + '/libs/qimessaging/2/qimessaging.js', function() {
            QiSession( resolve, reject, qimAddress );
        }).fail(function() {
            var error = "Failed to get qimessaging.js";
            if (robotIp) {
                error = error + " from robot: " + robotIp;
            } else {
                error = error + " from local domain; host this app on a robot or add a ?robot=MY-ROBOT-IP to the URL.";
            }
            reject(error);
        });
    });

    self._servicePromises = {};
    self.service = function(s) {
        return new Promise(function(resolve, reject) {
            if ( s in self._servicePromises ) {
                resolve( self._servicePromises[s] );
            } else {
                self.then(function(session) {
                    self._servicePromises[s] = session.service(s);
                    resolve( self._servicePromises[s] );
                }, function() {
                    reject("Failed getting " + s);
                });
            }
        });
    };

    function MemoryEventSubscription(event) {
        this._event = event;
        this._internalId = null;
        this._sub = null;
        this._unsubscribe = false;
    }

    MemoryEventSubscription.prototype.setId = function(id) {
        this._internalId = id;
        // as id can be receveid after unsubscribe call, defere
        if (this._unsubscribe) this.unsubscribe(this._unsubscribeCallback)
    }

    MemoryEventSubscription.prototype.setSubscriber = function(sub) {
        this._sub = sub;
        // as sub can be receveid after unsubscribe call, defere
        if (this._unsubscribe) this.unsubscribe(this._unsubscribeCallback)
    }

    MemoryEventSubscription.prototype.unsubscribe = function(unsubscribeDoneCallback)
    {
        if (this._internalId != null && this._sub != null) {
            evtSubscription = this;
            evtSubscription._sub.signal.disconnect(evtSubscription._internalId).then(function() {
                if (unsubscribeDoneCallback) unsubscribeDoneCallback();
            }, self.onQimError);
        }
        else
        {
            this._unsubscribe = true;
            this._unsubscribeCallback = unsubscribeDoneCallback;
        }
    }


    self.subscribeToEvent = function(event, eventCallback) {
        return new Promise(function(resolve, reject) {
            var evt = new MemoryEventSubscription(event);
            self.service("ALMemory").then( function(ALMemory) {
                ALMemory.subscriber(event).then( function (sub) {
                    evt.setSubscriber(sub);
                    sub.signal.connect(eventCallback).then( function(id) {
                        evt.setId(id);
                        resolve(evt);
                    },  reject);
                },  reject);
            });
        });
    }

    self.raiseEvent = function (event, data) {
        return new Promise(function(resolve, reject) {
            self.service("ALMemory").then( function(proxy) {
              proxy.raiseEvent(event, data).catch(reject);
            }).catch(reject);
        });
    }


    self.getData = function(key) {
        return new Promise(function(resolve, reject) {
            session.service("ALMemory").then( function(proxy) {
                proxy.getData(key).then(resolve, reject);
            });
        });
    }

    return self;


})(window.QimSession || {}, jQuery);

session.then(
    function(session) {
        console.log('Qimessaging: connected!');
    },
    function() {
        console.error('Qimessaging: disconnected!');
    }
);

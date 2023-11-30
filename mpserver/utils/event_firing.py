class EventFiring:
    """
    This class has event firing capabilities.
    You can implement this class when an Observer pattern needs to be used
    """
    def __init__(self):
        super(EventFiring, self).__init__()
        self._event_callbacks = {}
        for attr in [attr for attr in vars(self.__class__.Events) if not callable(attr) and not attr.startswith("__")]:
            self._event_callbacks[getattr(self.__class__.Events, attr)] = []

    def _fire_event(self, fire_event):
        # check if the fired event is in the registered events
        if fire_event in self._event_callbacks.keys():
            # get all callbacks from that event that are registered
            callbacks = self._event_callbacks[fire_event]
            # loop through all registered callbacks
            for callback in callbacks:
                if callable(callback):
                    # if the callback is callable then call it
                    callback()

    def subscribe(self, event, callback):
        if event in self._event_callbacks:
            self._event_callbacks[event].append(callback)

    class Events:
        pass

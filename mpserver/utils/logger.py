from datetime import datetime

from mpserver.utils.config import LOG
from mpserver.utils.tools import bugprint as b


class Logger:
    """
    The base class for all classes in mpserver package
    """
    def __init__(self):
        super(Logger, self).__init__()
        self._logging = True

    def log(self, content: object):
        if self._logging and LOG:
            b("[*" + str(self.__class__.__name__) + "* | " + datetime.now().strftime('%H:%M:%S') + "] " + str(content))

    def set_logging(self, state: bool):
        """ Set the logging state of this class
        If true then it's able to log else not

        :param state: True to turn on logging and False for off
        """
        self._logging = state

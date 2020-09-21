__author__ = 'wjjo'

import logging.handlers
import os
import socket
import subprocess
import sys
from abc import abstractmethod

import win32event
import win32service
import win32serviceutil
import win32timezone

assert win32timezone

import log

log.init()
basedir = os.path.dirname(__file__)


def handle_exception(f):
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logging.error(f'An error occurred while calling {f.__name__}', exc_info=e)

    return decorator


def trace(f):
    def decorator(*args, **kwargs):
        logging.debug(f'> {f.__name__}(...) // args: {str(args)} // kwargs : {str(kwargs)}')
        result = f(*args, **kwargs)
        logging.debug(f'< {f.__name__}(...) // return : {result}')
        return result

    return decorator


class WindowsService(win32serviceutil.ServiceFramework):
    """
    Base class to create Windows service in Python
    """

    @classmethod
    @trace
    @handle_exception
    def handle_command_line(cls):
        """
        ClassMethod to parse and run the command line
        """
        win32serviceutil.HandleCommandLine(cls)

    @trace
    @handle_exception
    def __init__(self, args):
        """
        Constructor of the service
        """

        try:
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            socket.setdefaulttimeout(60)
        except:
            logging.error('An error occurred.', exc_info=sys.exc_info())

    # noinspection PyPep8Naming
    @trace
    @handle_exception
    def SvcStop(self):
        """
        Called when the service is asked to stop
        """
        self._stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    # noinspection PyPep8Naming
    @trace
    @handle_exception
    def SvcDoRun(self):
        """
        Called when the service is asked to start
        """
        self._start()

    @trace
    @handle_exception
    @abstractmethod
    def _start(self):
        """
        Override to add logic before the start
        eg. running condition
        """
        pass

    @trace
    @handle_exception
    @abstractmethod
    def _stop(self):
        """
        Override to add logic before the stop
        eg. invalidating running condition
        """
        pass


class CommandLineBasedWindowsService(WindowsService):
    # noinspection SpellCheckingInspection
    _svc_name_ = ''
    _svc_display_name_ = ''
    _svc_description_ = ''

    @trace
    @handle_exception
    def __init__(self, *args, **kwargs):
        super(CommandLineBasedWindowsService, self).__init__(*args, **kwargs)

    @trace
    def _start(self):
        pass

    @trace
    def _stop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


class IncorrectUsageException(BaseException):
    pass


def main():
    CommandLineBasedWindowsService.handle_command_line()


if __name__ == '__main__':
    main()

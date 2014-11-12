import logging
import monkeysign.gpg

class Logger(object):
    def __init__(self):
        self.logger = logging.getLogger()


        # Monkeypatching monkeysign to get more debug output
        original_build_command = monkeysign.gpg.Context.build_command
        def patched_build_command(*args, **kwargs):
            return_value = original_build_command(*args, **kwargs)

            self.debug("Building cmd: %s", ' '.join(return_value))

            return return_value

        monkeysign.gpg.Context.build_command = patched_build_command

    def debug(self, *args):
        self.logger.debug(args)

    def info(self, *args):
        self.logger.info(args)

# Singleton logger instance
def get_instance():
    if '__logger' not in vars():
        __logger = Logger()

    return __logger

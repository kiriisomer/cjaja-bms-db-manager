import os
import errno
import datetime
from pathlib import Path
import logging


class Logger:
    logger = None
    def __init__(self, name=__name__, level=logging.DEBUG):
        """"""
        if not Logger.logger:
            self.__name = name
            Logger.logger = logging.getLogger(self.__name)
            Logger.logger.setLevel(level)

            Path("log").mkdir(parents=True, exist_ok=True)
            log_path = Path("log") / 'out.log'
            logname = str(log_path)
            # single logging file
            # fh = logging.FileHandler(logname, mode='a', encoding='utf-8')
            # multiple logging file separate by day
            fh = DayRotatingFileHandler(logname, mode='a', encoding='utf-8')
            fh.setLevel(level)

            ch = logging.StreamHandler()
            ch.setLevel(level)

            formatter = logging.Formatter('%(levelname)s %(asctime)s %(filename)s[%(lineno)d]'
                                        ': %(message)s',
                                        datefmt='%a %b%d %H:%M:%S')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            Logger.logger.addHandler(fh)
            Logger.logger.addHandler(ch)

    @staticmethod
    def get_logger():
        """"""
        return Logger.logger




class DayRotatingFileHandler(logging.FileHandler):
    def __init__(self, *args, **kwargs):
        self._time_counter = datetime.date.today()
        if args:
            self._baseFilename = args[0]
        else:
            self._baseFilename = kwargs["filename"]
        
        # self._rotate_at = self._next_rotate_datetime()
        super(DayRotatingFileHandler, self).__init__(*args, **kwargs)

    def _open(self):
        date_str = self._time_counter.strftime("%Y-%m-%d")
        a = Path(self._baseFilename)
        log_path = a.parent / ("_".join([a.stem , date_str]) + a.suffix)

        try:
            fd = os.open(log_path, os.O_CREAT | os.O_EXCL)
            # if coming here, the log file was created successfully
            os.close(fd)
        except OSError as e:
            if e.errno != errno.EEXIST:
                # should not happen
                raise

        self.baseFilename = log_path
        return super(DayRotatingFileHandler, self)._open()

    def emit(self, record):
        now_date = datetime.date.today()
        if self._time_counter != now_date:
            # time to rotate
            self._time_counter = now_date
            self.close()

        super(DayRotatingFileHandler, self).emit(record)


if __name__ == '__main__':
    log = Logger.get_logger()
    log.info('log test')

from logger import LoggerClass


logger_main = LoggerClass.LoggerClass('main')
logger_rabbit = LoggerClass.LoggerClass('rabbit')
logger_errors = LoggerClass.LoggerClass('errors')


def get_logger_main():
    return logger_main.get_logger()


def get_logger_rabbit():
    return logger_rabbit.get_logger()


def get_logger_errors():
    return logger_errors.get_logger()

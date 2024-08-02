from functools import wraps
from logger import loggerMain, loggerMongo
import sys
import os
import traceback
import datetime
from config import config

logger_main = loggerMain.get_logger()
logger_mongo = loggerMongo.get_logger()

MONGO = config.MONGO
mongo_slow_query_threshold = int(MONGO['slow_query_threshold'])


def catch_exceptions(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger_main.error("%s -- function %s -- args %s --kwargs %s -- line %s: %s",
                              os.path.split(traceback.extract_tb(exc_tb)[-1][0])[1], function.__name__, args, kwargs,
                              traceback.extract_tb(exc_tb)[-1][1], str(error))
    return decorator


def catch_exceptions_and_performance(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            start = datetime.datetime.now()
            result = function(*args, **kwargs)
            end = datetime.datetime.now()
            execution_time = ((end - start) * 1000).seconds
            logger_main.info("%s-%s-%d ms", os.path.split(function.__code__.co_filename)[1], function.__name__, execution_time)
            return result
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger_main.error("%s -- function %s -- line %s: %s", os.path.split(traceback.extract_tb(exc_tb)[-1][0])[1], function.__name__, traceback.extract_tb(exc_tb)[-1][1], str(error))
    return decorator


# --------- Mongo decorators ---------------


def mongo_catch_exceptions_and_performance(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            start = datetime.datetime.now()
            result = function(*args, **kwargs)
            end = datetime.datetime.now()
            execution_time = ((end - start) * 1000).seconds
            if execution_time > mongo_slow_query_threshold and 'filter' in kwargs:
                logger_mongo.warning("%s -- filter %s -- %s -- %d ms", kwargs['collection'], kwargs['filter'], function.__name__, execution_time)
            else:
                logger_mongo.info("%s -- %s -- %d ms", kwargs['collection'], function.__name__, execution_time)
            return result
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger_mongo.error("%s -- function %s -- line %s Args %s: %s", os.path.split(traceback.extract_tb(exc_tb)[-1][0])[1], function.__name__, traceback.extract_tb(exc_tb)[-1][1], str(kwargs), str(error))
            return None
    return decorator


def mongo_catch_exceptions(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger_mongo.error("%s -- function %s -- line %s: %s", os.path.split(traceback.extract_tb(exc_tb)[-1][0])[1], function.__name__, traceback.extract_tb(exc_tb)[-1][1], str(error))
            return None
    return decorator
from functools import wraps
import sys
import os
import traceback
import datetime
from logger import loggerGateway

loggerGateway = loggerGateway.get_logger()
# logger_mongo = loggerMongo.get_logger()

# MONGO = config.MONGO
# mongo_slow_query_threshold = int(MONGO['slow_query_threshold'])


def catch_exceptions(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            loggerGateway.error("%s -- function %s -- args %s --kwargs %s -- line %s: %s",
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
            loggerGateway.info("%s-%s-%d ms", os.path.split(function.__code__.co_filename)[1], function.__name__,
                               execution_time)
            return result
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            loggerGateway.error("%s -- function %s -- line %s: %s",
                                os.path.split(traceback.extract_tb(exc_tb)[-1][0])[1], function.__name__,
                                traceback.extract_tb(exc_tb)[-1][1], str(error))
    return decorator

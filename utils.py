import datetime

def time(fn):
    def timedFunction(*args, **kwargs):
        start_time = datetime.datetime.utcnow()
        fn_result = ''
        fn_result = fn(*args, **kwargs)
        print("`{}()` took {:.2f} ms to execute".format(fn.__name__, (datetime.datetime.utcnow() - start_time) 
            / datetime.timedelta(milliseconds=1)))
        return fn_result
        
    return timedFunction

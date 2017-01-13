class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_instance'):
            cls._instance=super(Singleton,cls).__new__(cls,*args,**kwargs)
            #print '11'
        #print '22'
        return cls._instance
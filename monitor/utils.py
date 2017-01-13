__author__ = 'baranbartu'

def import_object(object_path):
    """imports and returns given class string.

    :param object_path: Class path as string
    :type object_path: str

    :returns: Class that has given path
    :rtype: class

    :Example:

    >>> import_object('collections.OrderedDict').__name__
    'OrderedDict'
    """
    try:
        #from django.utils.importlib import import_module
        from importlib import import_module
        module_name = '.'.join(object_path.split(".")[:-1])
        mod = import_module(module_name)
        return getattr(mod, object_path.split(".")[-1])
    except Exception as detail:
        raise ImportError(detail)


def nested_method(clazz, method, nested):
    from types import CodeType, FunctionType
    """ Return the function named <child_name> that is defined inside
        a <parent> function
        Returns None if nonexistent
    """
    parent = getattr(clazz, method)
    consts = parent.func_code.co_consts
    for item in consts:
        if isinstance(item, CodeType) and item.co_name == nested:
            return FunctionType(item, globals())

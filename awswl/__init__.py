from usingversion import getattr_with_version

__getattr__ = getattr_with_version("mypackage", __file__, __name__)
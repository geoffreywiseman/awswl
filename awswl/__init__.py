from usingversion import getattr_with_version

__getattr__ = getattr_with_version("awswl", __file__, __name__)
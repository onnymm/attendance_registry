from ._core import env

class CONFIG:
    COOKIE = env.variable('COOKIE')
    DEVICE_MODEL = env.variable('DEVICE_MODEL')
    SITE_ID = env.variable('SITE_ID')
    TOKEN = env.variable('TOKEN')
    TIME_OFFSET = env.variable('TIME_OFFSET', int, 0)
    MAX_RESULTS_QTY = env.variable('MAX_RESULTS_QTY', int, 24)

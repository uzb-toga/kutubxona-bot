import config

def mask(s):
    if not s:
        return 'None'
    return s[:5] + '...' + s[-5:]

print("CONFIG LOADED")
print("PROXY:", config.PROXY)
print("REQUEST_TIMEOUT:", config.REQUEST_TIMEOUT)
print("TOKEN:", mask(config.TOKEN))

'''
Created on 8/02/2013

@author: konstaa
'''


SEVERITY_INFO    = 0x01
SEVERITY_WARNING = 0x02
SEVERITY_ERROR   = 0x03

def cout(path, cursor, level, message, details):
    notification = path + ":" + str(cursor) + ": "
    if level == SEVERITY_INFO:
        notification += "info: "
    elif level == SEVERITY_WARNING:
        notification += "warning: "
    elif level == SEVERITY_ERROR:
        notification += "error: "
    else:
        assert(len("Invalid message severity level specified") == 0)
    notification += message + "\n"

    DETAILS_OFFSET = 15
    for each in details:
        notification += "\t" + str(each[0]) + (" " * (DETAILS_OFFSET - len(each[0]))) + ": " + str(each[1]) + "\n"
        
    print notification

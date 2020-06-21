#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

SEVERITY_INFO    = 0x01
SEVERITY_WARNING = 0x02
SEVERITY_ERROR   = 0x03
DETAILS_OFFSET   = 15

def notify(path, cursor, level, message, details = [], indent = 0):
    notification = (".   " * indent) + path + ":" + (str(cursor) if cursor != None else "") + ": "
    if level == SEVERITY_INFO:
        notification += "info: "
    elif level == SEVERITY_WARNING:
        notification += "warning: "
    elif level == SEVERITY_ERROR:
        notification += "error: "
    else:
        assert(len("Invalid message severity level specified") == 0)
    notification += message + "\n"

    for each in details:
        notification += (("    " * indent) + "\t" +
                         str(each[0]) + (" " * (DETAILS_OFFSET - len(each[0]))) + ": " + str(each[1]) + "\n")
        
    print(notification)

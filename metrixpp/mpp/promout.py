#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import re

SEVERITY_INFO = 0x01
SEVERITY_WARNING = 0x02
SEVERITY_ERROR = 0x03
DETAILS_OFFSET = 15


def notify(path, metric, details, region=""):
    notification = ""

    for each in details:
        if str(each[1]) != 'None':
            if region:
                notification += ("{metric} {{file=\"{path}\", region=\"{region}\"}} {value}\n".format(metric=re.sub(r'^_', '', re.sub(r'[\.\:]', '_', metric + "." + str(each[0]))), value=str(each[1]), path=path, region=region))
            else:
                notification += ("{metric} {{file=\"{path}\"}} {value}\n".format(metric=re.sub(r'^_', '', re.sub(r'[\.\:]', '_', metric + "." + str(each[0]))), value=str(each[1]), path=path, region=region))
        
    print(notification)

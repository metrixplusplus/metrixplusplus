#
#    Metrix++, Copyright 2009-2013, Metrix++ Project
#    Link: http://metrixplusplus.sourceforge.net
#    
#    This file is a part of Metrix++ Tool.
#    
#    Metrix++ is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#    
#    Metrix++ is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with Metrix++.  If not, see <http://www.gnu.org/licenses/>.
#

SEVERITY_INFO    = 0x01
SEVERITY_WARNING = 0x02
SEVERITY_ERROR   = 0x03
DETAILS_OFFSET   = 15

def notify(path, cursor, level, message, details = [], indent = 0):
    notification = (".   " * indent) + path + ":" + str(cursor) + ": "
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
        
    print notification

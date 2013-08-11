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

import mpp.api

class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             # declare that it can subscribe on notifications
             mpp.api.Child):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        if self.is_active_numbers == True:
            # subscribe to notifications from all code parsers
            self.subscribe_by_parents_interface(mpp.api.ICode, 'callback')

    # parents (code parsers) will call the callback declared
    def callback(self, parent, data, is_updated):
        print parent.get_name(), data.get_path(), is_updated
        
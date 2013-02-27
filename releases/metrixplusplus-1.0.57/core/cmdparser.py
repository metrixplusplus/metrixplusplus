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

import optparse

class MultiOptionParser(optparse.OptionParser):
    
    class MultipleOption(optparse.Option):
        ACTIONS = optparse.Option.ACTIONS + ("multiopt",)
        STORE_ACTIONS = optparse.Option.STORE_ACTIONS + ("multiopt",)
        TYPED_ACTIONS = optparse.Option.TYPED_ACTIONS + ("multiopt",)
        ALWAYS_TYPED_ACTIONS = optparse.Option.ALWAYS_TYPED_ACTIONS + ("multiopt",)
    
        def take_action(self, action, dest, opt, value, values, parser):
            if action == "multiopt":
                values.ensure_value(dest, []).append(value)
            else:
                optparse.Option.take_action(self, action, dest, opt, value, values, parser)

    
    def __init__(self, *args, **kwargs):
        optparse.OptionParser.__init__(self, *args, option_class=self.MultipleOption, **kwargs)
        
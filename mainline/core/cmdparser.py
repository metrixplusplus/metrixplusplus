'''
Created on 8/02/2013

@author: konstaa
'''

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
        
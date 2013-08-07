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


import unittest

import tests.common

class Test(tests.common.TestCase):

    def test_basic(self):
        
        runner = tests.common.ToolRunner('collect', ['--std.suppress',
                                                     '--std.code.complexity.cyclomatic',
                                                     '--std.code.length.total',
                                                     '--std.general.size'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--max-limit=std.code.complexity:cyclomatic:0'],
                                         exit_code=1,
                                         prefix='1')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--max-limit=std.code.complexity:cyclomatic:0', '--disable-suppressions'],
                                         exit_code=8,
                                         prefix='2')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--max-limit=std.code.length:total:0'],
                                         exit_code=7,
                                         prefix='3')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--max-limit=std.code.length:total:0', '--disable-suppressions'],
                                         exit_code=26,
                                         prefix='4')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--max-limit=std.code.complexity:cyclomatic:0', '--max-limit=std.code.length:total:0'],
                                         exit_code=8,
                                         prefix='5')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--max-limit=std.general:size:0'],
                                         exit_code=0,
                                         prefix='size')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--max-limit=std.general:size:0', '--disable-suppressions'],
                                         exit_code=1,
                                         prefix='size_nosup')
        self.assertExec(runner.run())

if __name__ == '__main__':
    unittest.main()
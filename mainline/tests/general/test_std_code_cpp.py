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
import os

import tests.common

class Test(tests.common.TestCase):

    def test_parser(self):
        
        runner = tests.common.ToolRunner('collect', ['--std.code.complexity.cyclomatic'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', opts_list=['--format=xml'])
        self.assertExec(runner.run())
        
        dirs_list = [os.path.join('.', each) for each in os.listdir(self.get_content_paths().cwd)]
        runner = tests.common.ToolRunner('view', dirs_list=dirs_list, prefix='files')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--max-limit=std.code.complexity:cyclomatic:0'],
                                         exit_code=12)
        self.assertExec(runner.run())

if __name__ == '__main__':
    unittest.main()
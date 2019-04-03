#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import unittest
import os

import tests.common

class Test(tests.common.TestCase):

    def test_parser(self):
        
        runner = tests.common.ToolRunner('collect', ['--std.code.complexity.cyclomatic'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--nest-regions', '--format=xml'])
        self.assertExec(runner.run())

        dirs_list = [os.path.join('.', each) for each in os.listdir(self.get_content_paths().cwd)]
        runner = tests.common.ToolRunner('view',
                                         opts_list=['--nest-regions', '--format=txt'],
                                         dirs_list=dirs_list,
                                         prefix='files')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--max-limit=std.code.complexity:cyclomatic:5'],
                                         exit_code=6)
        self.assertExec(runner.run())

if __name__ == '__main__':
    unittest.main()
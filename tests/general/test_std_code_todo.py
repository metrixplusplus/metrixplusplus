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

    def test_comments(self):
        
        runner = tests.common.ToolRunner('collect', ['--std.code.todo.comments'])
        self.assertExec(runner.run())

        dirs_list = [os.path.join('.', each) for each in os.listdir(self.get_content_paths().cwd)]
        runner = tests.common.ToolRunner('view',
                                         opts_list=['--nest-regions', '--format=txt'],
                                         dirs_list=dirs_list,
                                         prefix='files')
        self.assertExec(runner.run())

    def test_strings(self):
        
        runner = tests.common.ToolRunner('collect', ['--std.code.todo.strings'])
        self.assertExec(runner.run())

        dirs_list = [os.path.join('.', each) for each in os.listdir(self.get_content_paths().cwd)]
        runner = tests.common.ToolRunner('view',
                                         opts_list=['--nest-regions', '--format=txt'],
                                         dirs_list=dirs_list,
                                         prefix='files')
        self.assertExec(runner.run())

    def test_tags(self):
        
        runner = tests.common.ToolRunner('collect', ['--sctc', '--scts',
                                                     '--std.code.todo.tags=FIX-ME,FIXME'],
                                         exit_code=2,
                                         prefix='badtag',
                                         check_stderr=[(0, -1)])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('collect', ['--sctc', '--scts',
                                                     '--std.code.todo.tags=TOBEDONE,TODO,FIXME'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',)
        self.assertExec(runner.run())

if __name__ == '__main__':
    unittest.main()
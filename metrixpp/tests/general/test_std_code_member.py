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

    def test_fields(self):

        runner = tests.common.ToolRunner('collect', ['--std.code.member.fields'])
        self.assertExec(runner.run())

        dirs_list = [os.path.join('.', each) for each in sorted(os.listdir(self.get_content_paths().cwd))]
        runner = tests.common.ToolRunner('view',
                                         opts_list=['--nest-regions', '--format=txt'],
                                         dirs_list=dirs_list,
                                         prefix='files')
        self.assertExec(runner.run())

    def test_globals(self):

        runner = tests.common.ToolRunner('collect', ['--std.code.member.globals'])
        self.assertExec(runner.run())

        dirs_list = [os.path.join('.', each) for each in sorted(os.listdir(self.get_content_paths().cwd))]
        runner = tests.common.ToolRunner('view',
                                         opts_list=['--nest-regions', '--format=txt'],
                                         dirs_list=dirs_list,
                                         prefix='files')
        self.assertExec(runner.run())

    def test_methods(self):

        runner = tests.common.ToolRunner('collect', ['--std.code.member.methods'])
        self.assertExec(runner.run())

        dirs_list = [os.path.join('.', each) for each in sorted(os.listdir(self.get_content_paths().cwd))]
        runner = tests.common.ToolRunner('view',
                                         opts_list=['--nest-regions', '--format=txt'],
                                         dirs_list=dirs_list,
                                         prefix='files')
        self.assertExec(runner.run())


if __name__ == '__main__':
    unittest.main()

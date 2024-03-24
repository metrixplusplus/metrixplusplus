#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import unittest

import tests.common

class Test(tests.common.TestCase):

    def test_workflow(self):
        
        # first collection
        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.complexity.cyclomatic',
                                          '--std.code.lines.total',
                                          '--std.code.lines.code',
                                          '--std.code.lines.preprocessor',
                                          '--std.code.lines.comments',
                                          '--std.code.ratio.comments',
                                          '--std.suppress',
                                          '--log-level=INFO'],
                                         check_stderr=[(0, -1)],
                                         save_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--log-level=INFO', '--format=xml'],
                                         check_stderr=[(0, -1)])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--log-level=INFO',
                                          '--max-limit=std.code.complexity:cyclomatic:0'],
                                         check_stderr=[(0, -1)],
                                         exit_code=8)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('info',
                                         ['--log-level=INFO'],
                                         check_stderr=[(0, -1)],
                                         exit_code=0)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('export',
                                         ['--log-level=INFO'],
                                         check_stderr=[(0, -1)])
        self.assertExec(runner.run())

        # second collection
        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.complexity.cyclomatic',
                                          '--std.code.lines.total',
                                          '--std.code.lines.code',
                                          '--std.code.lines.preprocessor',
                                          '--std.code.lines.comments',
                                          '--std.code.ratio.comments',
                                          '--std.suppress',
                                          '--log-level=INFO'],
                                         check_stderr=[(0, -1)],
                                         prefix='second',
                                         cwd="sources_changed",
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--log-level=INFO', '--format=xml'],
                                         check_stderr=[(0, -1)],
                                         prefix='second',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--log-level=INFO', '--format=xml'],
                                         check_stderr=[(0, -1)],
                                         prefix='second_per_file',
                                         dirs_list=['./simple.cpp'],
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--log-level=INFO', '--scope-mode=all'],
                                         check_stderr=[(0, -1)],
                                         prefix='second_txt_all',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--log-level=INFO', '--scope-mode=all'],
                                         check_stderr=[(0, -1)],
                                         prefix='second_per_file_txt_all',
                                         dirs_list=['./simple.cpp'],
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--log-level=INFO', '--scope-mode=touched'],
                                         check_stderr=[(0, -1)],
                                         prefix='second_txt_touched',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--log-level=INFO', '--scope-mode=touched'],
                                         check_stderr=[(0, -1)],
                                         prefix='second_per_file_txt_touched',
                                         dirs_list=['./simple.cpp'],
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--log-level=INFO', '--scope-mode=new'],
                                         check_stderr=[(0, -1)],
                                         prefix='second_txt_new',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--log-level=INFO', '--scope-mode=new'],
                                         check_stderr=[(0, -1)],
                                         prefix='second_per_file_txt_new',
                                         dirs_list=['./simple.cpp'],
                                         use_prev=True)
        self.assertExec(runner.run())


        runner = tests.common.ToolRunner('limit',
                                         ['--log-level=INFO',
                                          '--max-limit=std.code.complexity:cyclomatic:0'],
                                         check_stderr=[(0, -1)],
                                         exit_code=6,
                                         prefix='second',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--log-level=INFO',
                                          '--max-limit=std.code.complexity:cyclomatic:0',
                                          '--warn-mode=all'],
                                         check_stderr=[(0, -1)],
                                         exit_code=6,
                                         prefix='second_warn_all',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--log-level=INFO',
                                          '--max-limit=std.code.complexity:cyclomatic:0',
                                          '--warn-mode=touched'],
                                         check_stderr=[(0, -1)],
                                         exit_code=4,
                                         prefix='second_warn_touched',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--log-level=INFO',
                                          '--max-limit=std.code.complexity:cyclomatic:0',
                                          '--warn-mode=trend'],
                                         check_stderr=[(0, -1)],
                                         exit_code=3,
                                         prefix='second_warn_trend',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit',
                                         ['--log-level=INFO',
                                          '--max-limit=std.code.complexity:cyclomatic:0',
                                          '--warn-mode=new'],
                                         check_stderr=[(0, -1)],
                                         exit_code=2,
                                         prefix='second_warn_new',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('info',
                                         ['--log-level=INFO'],
                                         check_stderr=[(0, -1)],
                                         prefix='second',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('export',
                                         ['--log-level=INFO'],
                                         check_stderr=[(0, -1)],
                                         prefix='second',
                                         use_prev=True)
        self.assertExec(runner.run())

    def test_help(self):
        
        runner = tests.common.ToolRunner('--help')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('unknown', exit_code=2)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('collect', ['--help'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('info', ['--help'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--help'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('limit', ['--help'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('export', ['--help'])
        self.assertExec(runner.run())

    def test_exclusion(self):

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.complexity.cyclomatic',
                                          '--exclude-files=simple_excluded'],
                                         prefix='excluding-unused',
                                         check_stderr=[(0, -1)],
                                         cwd="sources_exclude")
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.complexity.cyclomatic',
                                          '--exclude-directories=.*\/excluded'],
                                         prefix='excluding-directories',
                                         check_stderr=[(0, -1)],
                                         cwd="sources_exclude")
        self.assertExec(runner.run())

    def test_view_format(self):
        
        # note: --scope-mode is tested in workflow test above

        runner = tests.common.ToolRunner('collect', ['--std.code.complexity.cyclomatic'], save_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--format=txt'], prefix='txt')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--format=python'], prefix='python')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--format=xml'], prefix='xml')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--format=prometheus', '--log-level=ERROR'], prefix='prometheus')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--format=prometheus', '--log-level=ERROR'],
                                         prefix='prometheus_simple.cpp',
                                         dirs_list=['./simple.cpp'])
        self.assertExec(runner.run())
        
        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.complexity.cyclomatic'],
                                         prefix='nest',
                                         cwd="sources_changed",
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions', '--format=xml'],
                                         prefix='nest',
                                         use_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions', '--format=xml'],
                                         prefix='nest_per_file',
                                         dirs_list=['./simple.cpp'],
                                         use_prev=True)
        self.assertExec(runner.run())

    def test_report_format(self):

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.complexity.cyclomatic',
                                          '--std.code.lines.total',
                                          '--std.code.lines.code',
                                          '--std.code.filelines.total'],
                                         save_prev=True)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('report',
                                         ['--format=txt', '--max-limit=std.code.complexity:cyclomatic:0'],
                                         prefix='txt')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('report',
                                         ['--format=json', '--max-limit=std.code.complexity:cyclomatic:0'],
                                         prefix='json')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('report',
                                         ['--format=doxygen', '--max-limit=std.code.complexity:cyclomatic:0'],
                                         prefix='dox')
        self.assertExec(runner.run())

    def test_std_general_metrics(self):

        runner = tests.common.ToolRunner('collect',
                                         ['--std.general.size',
                                          '--std.general.procerrors',
                                          '--std.general.proctime'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--format=txt'], prefix='txt')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions', '--format=txt'],
                                         prefix='nest_per_file',
                                         dirs_list=['./simple.cpp'])
        self.assertExec(runner.run())

    def test_std_lines_metrics(self):

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.lines.code',
                                          '--std.code.lines.preprocessor',
                                          '--std.code.lines.comments',
                                          '--std.code.ratio.comments',
                                          '--std.code.lines.total'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions', '--format=txt'],
                                         prefix='nest_per_file',
                                         dirs_list=['./simple.cpp'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--format=txt'], prefix='txt')
        self.assertExec(runner.run())

    def test_std_filelines_metrics(self):

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.filelines.code',
                                          '--std.code.filelines.preprocessor',
                                          '--std.code.filelines.comments',
                                          '--std.code.filelines.total'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions', '--format=txt'],
                                         prefix='nest_per_file',
                                         dirs_list=['./simple.cpp'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--format=txt'], prefix='txt')
        self.assertExec(runner.run())

    def test_std_longlines_metrics(self):

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.longlines',
                                          '--std.code.longlines.limit=50'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions', '--format=txt'],
                                         prefix='nest_per_file',
                                         dirs_list=['./simple.cpp'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--format=txt'], prefix='txt')
        self.assertExec(runner.run())

    def test_std_complexity_maxindent(self):

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.complexity.maxindent'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions'],
                                         prefix='nest_per_file',
                                         dirs_list=['./simple.cpp'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view')
        self.assertExec(runner.run())

    def test_std_code_magic(self):

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.magic.numbers'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions'],
                                         prefix='nest_per_file',
                                         dirs_list=['./simple.cpp'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view')
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.magic.numbers', '--std.code.magic.numbers.simplier'],
                                         prefix='nozeros',)
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions'],
                                         prefix='nozeros_nest_per_file',
                                         dirs_list=['./simple.cpp'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', prefix='nozeros')
        self.assertExec(runner.run())

    def test_std_member_metrics(self):

        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.member.fields',
                                          '--std.code.member.globals',
                                          '--std.code.member.classes',
                                          '--std.code.member.structs',
                                          '--std.code.member.interfaces',
                                          '--std.code.member.types',
                                          '--std.code.member.methods',
                                          '--std.code.member.namespaces'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view',
                                         ['--nest-regions', '--format=txt'],
                                         prefix='nest_per_file',
                                         dirs_list=['./simple.cpp'])
        self.assertExec(runner.run())

        runner = tests.common.ToolRunner('view', ['--format=txt'], prefix='txt')
        self.assertExec(runner.run())

    def test_std_maintindex(self):
        runner = tests.common.ToolRunner('collect',
                                         ['--std.code.complexity.cyclomatic',
                                          '--std.code.lines.code',
                                          '--std.code.maintindex.simple',
                                          '--log-level=INFO'],
                                         check_stderr=[(0, -1)],
                                         save_prev=True)
        self.assertExec(runner.run())
        runner = tests.common.ToolRunner('view', ['--format=txt'], prefix='txt')
        self.assertExec(runner.run())

if __name__ == '__main__':
    unittest.main()

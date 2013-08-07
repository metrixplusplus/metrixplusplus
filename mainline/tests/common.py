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

import inspect
import os.path
import subprocess
import logging
import difflib
import unittest
import shutil

class ToolRunner(object):

    def __init__(self,
                 tool_name,
                 opts_list = [],
                 dirs_list = None,
                 cwd='sources',
                 prefix = "default",
                 exit_code = 0,
                 save_prev = False,
                 use_prev = False,
                 check_stderr = None,
                 remove_exiting_dbfile = None,
                 remove_exiting_dbfile_prev = False):
        
        self.message = ""
        
        # identify gold_file_location
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        test_name = calframe[1][3]
        suite_name = os.path.splitext(os.path.basename(calframe[1][1]))[0]
        group_name = os.path.basename(os.path.dirname(calframe[1][1]))

        self.suite_location = os.path.join('tests', group_name, suite_name) 
        self.test_location = os.path.join(self.suite_location, test_name + "_" + tool_name + "_" + str(prefix))

        db_file = os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], self.suite_location, test_name + ".db")
        self.dbfile = db_file
        if (remove_exiting_dbfile == True or (remove_exiting_dbfile == None and tool_name == 'collect')) and os.path.exists(db_file):
            os.unlink(db_file)
        
        db_file_prev = os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], self.suite_location, test_name + ".prev.db")
        self.dbfile_prev = db_file_prev
        if (remove_exiting_dbfile_prev == True or (remove_exiting_dbfile_prev == None and tool_name == 'collect')) and os.path.exists(db_file_prev):
            os.unlink(db_file_prev)

        self.cwd = cwd

        db_opts = ['--db-file=' + db_file]
        if use_prev == True:
            db_opts.append('--db-file-prev=' + db_file_prev)
        self.dbopts = db_opts
        
        self.dirs_list = [] 
        if dirs_list != None:
            for each in dirs_list:
                self.dirs_list.append(each)
               
        self.call_args = ['python', os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], "metrix++.py"), tool_name] \
                    + db_opts + opts_list + ['--'] + self.dirs_list
        self.cmd = " ".join(self.call_args)
        self.exit_code_expected = exit_code
        self.stderr_lines = check_stderr
        self.save_prev = save_prev
        
    def run(self):
        logging.debug(self.get_description())
        child = subprocess.Popen(self.call_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 cwd=os.path.join(self.suite_location, self.cwd))
        (child_stdout, child_stderr) =  child.communicate()
        self.exit_code = child.returncode

        gold_file_stdout = self.test_location + "_stdout.gold.txt"
        real_file_stdout = self.test_location + "_stdout.real.txt"
        diff_file_stdout = self.test_location + "_stdout.diff.html"
        gold_file_stderr = self.test_location + "_stderr.gold.txt"
        real_file_stderr = self.test_location + "_stderr.real.txt"
        diff_file_stderr = self.test_location + "_stderr.diff.html"

        # Regenerate gold files if it was requested
        if os.environ['METRIXPLUSPLUS_TEST_GENERATE_GOLDS'] == "True":
            f = open(gold_file_stdout, 'wb');
            f.write(child_stdout);
            f.close()
            if self.stderr_lines != None:
                f = open(gold_file_stderr, 'wb');
                f.write(child_stderr);
                f.close()

        # Match with gold        
        self.is_stdout_matched = self.inetrnal_compare_with_gold(child_stdout, gold_file_stdout, real_file_stdout, diff_file_stdout)
        if self.stderr_lines != None:
            self.is_stderr_matched = self.inetrnal_compare_with_gold(child_stderr, gold_file_stderr, real_file_stderr, diff_file_stderr, self.stderr_lines)
        else:
            self.is_stderr_matched = None
            if self.is_stdout_matched == False:
                f = open(real_file_stderr, 'wb');
                f.write(child_stderr);
                f.close()
            else:
                if os.path.exists(real_file_stderr):
                    os.unlink(real_file_stderr)


        if self.save_prev == True:
            shutil.copy2(self.dbfile, self.dbfile_prev)                
        return self

    def inetrnal_compare_with_gold(self, text, gold_file, real_file, diff_file, lines = None):
        if os.path.exists(gold_file) == False:
            self.message += "\nGold file does not exist: " + gold_file
            return False
        
        f = open(gold_file, 'rb');
        gold_text = f.read();
        f.close()

        gold_to_compare = gold_text
        text_to_compare = text
        if lines != None:
            gold_to_compare = ""
            text_to_compare = ""
            gold_lines = gold_text.splitlines(True)
            text_lines = text.splitlines(True)
            for each in lines:
                gold_to_compare += "".join(gold_lines[each[0] : each[1]])
                text_to_compare += "".join(text_lines[each[0] : each[1]])
            
        result = (gold_to_compare == text_to_compare)
        
        if result == False:
            f = open(real_file, 'wb');
            f.write(text);
            f.close()
            
            diff_text = difflib.HtmlDiff().make_file(gold_to_compare.splitlines(), text_to_compare.splitlines(), "Gold file", "Real output")
            f = open(diff_file, 'w');
            f.write(diff_text);
            f.close()
        else:
            if os.path.exists(real_file):
                os.unlink(real_file)
            if os.path.exists(diff_file):
                os.unlink(diff_file)
        return result 
    
    def check_exit_code(self):
        return self.exit_code == self.exit_code_expected

    def check_stdout(self):
        return self.is_stdout_matched

    def check_stderr(self):
        if self.is_stderr_matched == None:
            return True
        return self.is_stderr_matched

    def check_all(self):
        result = self.check_exit_code() and self.check_stdout() and self.check_stderr()
        if result == False:
            self.message += "\nCheck for exit code: " + str(self.check_exit_code()) \
             + ", gold: " + str(self.exit_code_expected)  + ", real: " + str(self.exit_code) + \
             "\nCheck for stdout: " + str(self.check_stdout()) + "\nCheck for stderr: " + str(self.check_stderr())
        return result
    
    def get_message(self):
        return self.message
    
    def get_cmd(self):
        return self.cmd    

    def get_description(self):
        return self.get_message() + "\nProcess: " + self.get_cmd()  + "\nCWD: " + os.path.join(self.suite_location, self.cwd)       

    def get_dbfile(self):
        return self.dbfile

    def get_dbfile_prev(self):
        return self.dbfile_prev
    
class TestCase(unittest.TestCase):
    
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName=methodName)
        if 'METRIXPLUSPLUS_LOG_LEVEL' not in os.environ.keys():
            # launch of individual unit test
            os.environ['METRIXPLUSPLUS_LOG_LEVEL'] = 'ERROR'
            os.environ['METRIXPLUSPLUS_INSTALL_DIR'] = os.path.dirname(os.path.dirname(__file__))
            os.environ['METRIXPLUSPLUS_TEST_MODE'] = str("True")
            if 'METRIXPLUSPLUS_TEST_GENERATE_GOLDS' not in os.environ.keys():
                os.environ['METRIXPLUSPLUS_TEST_GENERATE_GOLDS'] = str("False")
            os.chdir(os.environ['METRIXPLUSPLUS_INSTALL_DIR'])

    def get_content_paths(self, cwd='sources'): 
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        test_name = calframe[1][3]
        suite_name = os.path.splitext(os.path.basename(calframe[1][1]))[0]
        group_name = os.path.basename(os.path.dirname(calframe[1][1]))
        
        class ContentPaths(object):
            
            def __init__(self, cwd, dbfile, dbfile_prev):
                self.cwd = cwd
                self.dbfile = dbfile
                self.dbfile_prev = dbfile_prev
                
        return ContentPaths(os.path.join('tests', group_name, suite_name, cwd),
                            os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], 'tests', group_name, suite_name, test_name + ".db"),
                            os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], 'tests', group_name, suite_name, test_name + ".prev.db"))

    def setUp(self):
        unittest.TestCase.setUp(self)

        logging.basicConfig(format="[TEST-LOG]: %(levelname)s:\t%(message)s", level=logging.WARN)

        log_level = os.environ['METRIXPLUSPLUS_LOG_LEVEL']
        if log_level == 'ERROR':
            log_level = logging.ERROR
        elif log_level == 'WARNING':
            log_level = logging.WARNING
        elif log_level == 'INFO':
            log_level = logging.INFO
        elif log_level == 'DEBUG':
            log_level = logging.DEBUG
        else:
            raise AssertionError("Unhandled choice of log level")
        logging.getLogger().setLevel(log_level)
        
        self.runners = []
        
    def assertExec(self, runner):
        # keep reference, so files are not removed during test case time
        self.runners.append(runner)
        self.assertTrue(runner.check_all(), runner.get_description())
        
    def run(self, result=None):
        self.current_result = result # remember result for use in tearDown
        unittest.TestCase.run(self, result)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        if self.current_result.wasSuccessful() == True:
            for each in self.runners:
                if each.check_all() == True:
                    if os.path.exists(each.get_dbfile()):
                        os.unlink(each.get_dbfile())
                    if os.path.exists(each.get_dbfile_prev()):
                        os.unlink(each.get_dbfile_prev())

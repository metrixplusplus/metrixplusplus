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
import subprocess
import os.path

class TestGeneralCollect(unittest.TestCase):

    def setUp(self):
        pass

    def test_default(self):
        ret_code = subprocess.call(['python', os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], 'collect.py'), '--help'])
        self.assertEqual(ret_code, 0)

if __name__ == '__main__':
    unittest.main()
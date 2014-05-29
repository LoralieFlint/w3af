"""
test_strategy.py

Copyright 2012 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import subprocess
import sys
import os

from nose.plugins.attrib import attr

from w3af.core.controllers.ci.moth import get_moth_http
from w3af.core.controllers.ci.wavsep import get_wavsep_http
from w3af.plugins.tests.helper import PluginTest, PluginConfig

SCRIPT_PATH = '/tmp/script-1557.w3af'
TEST_SCRIPT_1557 = """\
plugins
output console
output config console
set verbose False
back

audit xss

crawl web_spider
crawl config web_spider
set only_forward True
back

back
target
set target %s/active/RXSS-Detection-Evaluation-GET/index.jsp
back

start

exit
"""


class TestStrategy(PluginTest):
    target_url = get_moth_http('/audit/sql_injection/'
                               'where_string_single_qs.py?uname=pablo')

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'audit': (PluginConfig('sqli'),),
            }
        }
    }

    @attr('smoke')
    @attr('moth')
    def test_same_fr_set_object(self):
        cfg = self._run_configs['cfg']

        id_before_fr = id(self.kb.get_all_known_fuzzable_requests())
        id_before_ur = id(self.kb.get_all_known_urls())
        
        self._scan(cfg['target'], cfg['plugins'])
        
        id_after_fr = id(self.kb.get_all_known_fuzzable_requests())
        id_after_ur = id(self.kb.get_all_known_urls())

        self.assertEquals(id_before_fr, id_after_fr)
        self.assertEquals(id_before_ur, id_after_ur)

    def tearDown(self):
        if os.path.exists(SCRIPT_PATH):
            os.unlink(SCRIPT_PATH)

    def test_1557_random_number_of_results(self):
        """
        Pseudo-random number of vulnerabilities found in audit phase (xss)

        https://github.com/andresriancho/w3af/issues/1557
        """
        file(SCRIPT_PATH, 'w').write(TEST_SCRIPT_1557 % get_wavsep_http())

        python_executable = sys.executable

        VULN_STRING = 'A Cross Site Scripting vulnerability'
        vuln_count = []

        for i in xrange(25):
            print('Start run #%s' % i)

            p = subprocess.Popen([python_executable, 'w3af_console',
                                  '-n', '-s', script_path],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  shell=False,
                                  universal_newlines=True)

            stdout, stderr = p.communicate()
            i_vuln_count = stdout.count(VULN_STRING)
            print('%s vulnerabilities found' % i_vuln_count)

            self.assertNotEqual(i_vuln_count, 0)

            for previous_count in vuln_count:
                self.assertEqual(previous_count, i_vuln_count)

            vuln_count.append(i_vuln_count)

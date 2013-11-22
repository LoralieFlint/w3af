'''
test_global_redirect.py

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
'''
from nose.plugins.attrib import attr

from w3af.core.controllers.ci.moth import get_moth_http
from w3af.plugins.tests.helper import PluginTest, PluginConfig


class TestGlobalRedirect(PluginTest):

    target_url = '%s/audit/global_redirect/' % get_moth_http()

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'audit': (PluginConfig('global_redirect'),),
                'crawl': (
                    PluginConfig(
                        'web_spider',
                        ('only_forward', True, PluginConfig.BOOL)),
                )

            }
        },
    }

    def test_found_redirect(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        vulns = self.kb.get('global_redirect', 'global_redirect')

        self.assertEquals(all(['Insecure redirection' == vuln.get_name(
        ) for vuln in vulns]), True)

        # Verify the specifics about the vulnerabilities
        EXPECTED = [
            ('redirect-javascript.py', 'url'),
            ('redirect-meta.py', 'url'),
            ('redirect-302.py', 'url'),
            ('redirect-header-302.py', 'url'),
            ('redirect-302-filtered.py', 'url')
        ]

        found = [(str(v.get_url()), v.get_var()) for v in vulns]
        expected = [((self.target_url + end), param) for (end,
                    param) in EXPECTED]

        self.assertEquals(
            set(found),
            set(expected)
        )

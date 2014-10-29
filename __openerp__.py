# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Cyril MORISSE - @cmorisse
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Inouk Server Detect',
    'version': '0.1',   # Eg. 0.1 : Warning used for migration scripts
    'author': 'Cyril MORISSE - @cmorisse',
    'category': 'Inouk',
    'description': """
Detects which kind of server is running base on ip address and update a set of
variables accordingly:
    - openerp.ik_sd_is_production_server = True | False
    - openerp.ik_sd_is_staging_server = True | False
    - openerp.ik_sd_is_test_server = True | False
    - openerp.ik_sd_detected_ip = current_ip
    - openerp.ik_sd_server_kind = 'staging' | 'production' | 'test'.

Configuration
-------------
    Add these lines to your buildout.cfg:

    #
    # Inouk Server Detect Configution
    #
    options.ik_sd_production_servers_ips = server.domain.ext
    options.ik_sd_staging_servers_ips = 1.3.4.5,56.34.56.67

""",
    'website': '',
    'images': [],
    'depends': [
    ],
    'data': [
    ],
    'js': [],
    'qweb': [],
    'css': [],
    'demo': [],
    'test': [],
    'post_load': 'server_detect',
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

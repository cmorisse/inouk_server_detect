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
variables:

- openerp.ik_sd_is_production_server = True | False
- openerp.ik_sd_is_staging_server = True | False
- openerp.ik_sd_is_test_server = True | False
- openerp.ik_sd_detected_ip = current_ip
- openerp.ik_sd_server_kind = 'staging' | 'production' | 'development'.

iksd can optionnaly modify some server settings based on the server type:

Server settings available for modification
------------------------------------------

Ribbon
======

If the option `ik_sd_update_ribbon` is True and the module OCA web_environment_ribbon is installed,
then the ribbon will be updated:

- production: No Ribbon 
- staging : With on Red
- test/dev : White on Purple

Technically, iksd updates the config parameter used by the module `web_environment_ribbon' in all databases 
specified by the -d --database parameter.


Cron deactivation
=================

If the server is not a production one, the option `ik_sd_deactivate_cron` value allows  to deactivate 
some crons.
we desactivate some crons. The ik_sd_cron_id options can contains :

- One cron ID like this (>8): desactivate all crons having ID > 8.
- List of IDs separated by comma: desactivate all crons with those IDs.
- List of External IDs separated by comma: desactivate all crons with those external IDs.


Reset Passwords
===============

The options `ik_sd_development_passwords` and `ik_sd_development_passwords` allows to 
specify a password that will be let to all users depending on detected server kind.

Mail rerouting
==============

The option `ik_sd_email_debug_recipients` allows to specify a list of email addresses
that will receive all sent email.



Configuration
-------------


::

  Add these lines to your buildout.cfg:

  #
  # Inouk Server Detect Configuration
  #
  options.ik_sd_production_servers_ips = 1.2.3.4,14.5.6.86
  options.ik_sd_staging_servers_ips = 1.3.4.5,56.34.56.67
  options.ik_sd_update_ribbon = True
  options.ik_sd_ribbon_name = Cyril's Dev Server
  
  options.ik_sd_disable_cron = >8 | 9,5,7 | cron1,cust_cron
  options.ik_sd_development_passwords = Easy
  #options.ik_sd_staging_passwords =  # Password won't be modified on staging.
  options.ik_sd_email_debug_recipients = cmo@domain.ext,jfk@dom2.com

""",
    'website': '',
    'images': [],
    'depends': [
    ],
    'data': [
    ],
    'post_load': 'server_detect',
    'installable': True,
    'auto_install': False,
    'application': False,
}

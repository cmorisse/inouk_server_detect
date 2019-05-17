import shutil
import os
import sys
import socket
import logging
import json
import urllib2
import threading
import cgi

__author__ = 'cmorisse'
import openerp

_logger = logging.getLogger('iksd')

def get_databases():
    db_names = []
    if openerp.tools.config['db_name']:
        db_names = openerp.tools.config['db_name'].split(',')
    return db_names
    

def get_cursor(db_name):
    """ returns a Cursor for `db_name`.

    Once created cursor can be used with:
       - cr.execute(query)
       - cr.commit()
       - cr.rollback()

    Finally Cursor must be explicitly closed with:
       - cr.close()
    """
    registries = openerp.modules.registry.RegistryManager.registries.iteritems()
    db_names = [r[0] for r in registries]
    if db_name in db_names:
        db_connection = openerp.sql_db.db_connect(db_name)
        return db_connection.cursor()
    return None


def get_public_ip():
    """ Retrieve server public IP using 2 sources from
    https://stackoverflow.com/questions/9481419/how-can-i-get-the-public-ip-using-python2-7
    """
    try:
        ip = urllib2.urlopen('https://api.ipify.org').read()
    except:
        try:
            ip = json.load(urllib2.urlopen('http://httpbin.org/ip'))['origin']
        except:
            _logger.critical("Unable to retrieve public IP for server.")
            return None
    return ip


def update_ribbon():
    """ If module `web_environment_ribbon`is installed and `ik_sd_update_ribbon` is True
    update Ribbon color, background and text accoding to serveur kind and option
    `ik_sd_ribbon_name` parameters.
    """
    # TODO: Allow users to customize colors and text
    ribbon_colors = {
        #'server_kind': ('ribbon.color', 'ribbon.background.color')
        'production': ('Production', '#F0F0F0', 'rgba(255,0,0,.6)'),
        'staging': ('Staging', '#FFFFFF', 'rgba(253,98,10,.8)'),
        'development': ('Development', '#FDFDFD', 'rgba(253,98,10,.8)'),
    }
    
    if openerp.tools.config.options.get('ik_sd_update_ribbon', None):
        ribbon_data = ribbon_colors[openerp.ik_sd_server_kind]
        ribbon_name = cgi.escape(openerp.tools.config.options.get('ik_sd_ribbon_name', ribbon_data[0]))
        ribbon_color = ribbon_data[1]
        ribbon_background_color = ribbon_data[2]

        db_names = get_databases()
        for db_name in db_names:
            cr = get_cursor(db_name)
            try:
                if openerp.ik_sd_server_kind == 'production':
                    cr.execute("UPDATE ir_config_parameter SET key = 'ribbon.name.disabled' WHERE key='ribbon.name'");
                else:
                    cr.execute("UPDATE ir_config_parameter SET key = 'ribbon.name' WHERE key='ribbon.name.disabled'");
                    cr.execute("UPDATE ir_config_parameter SET value = '%s' WHERE key='ribbon.name'" % ribbon_name);
                cr.execute("UPDATE ir_config_parameter SET value = '%s' WHERE key='ribbon.color'" % ribbon_color);
                cr.execute("UPDATE ir_config_parameter SET value = '%s' WHERE key='ribbon.background.color'" % ribbon_background_color);
                cr.commit()
            finally:
                cr.close()
            _logger.info("Ribbon updated in database: \'%s\' with name: '%s'" % (db_name, ribbon_name,))


def reset_passwords():
    server_type = openerp.ik_sd_server_kind
    option_name = "ik_sd_%s_passwords" % server_type
    new_password = openerp.tools.config.options.get(option_name, None)
    
    if openerp.ik_sd_is_production_server:
        _logger.info("Ignoring password management on production servers.")
        return 
    
    # reset password only works on provided databases list
    db_names = get_databases()
    if new_password:
        if db_names:
            for db_name in db_names:
                try:
                    cr = get_cursor(db_name)
        
                    #sql = "UPDATE res_users SET password='%s' WHERE id != 1;" % new_password
                    sql = "UPDATE res_users SET password='%s';" % new_password
                    cr.execute(sql)
                    cr.commit()
        
                    _logger.info("Resetting all users password with '%s' on database: %s", 
                                 new_password,
                                 db_name)
                finally:
                    cr.close()
        else:
            _logger.critical("Odoo launched with '%s' option but no databases specified. Aborting." % option_name)
            os._exit(1)
            
    else:
        _logger.info("'ik_sd_test_password' option not set or no databases list specified.")



def disable_crons():
    """ Disable CRONs sepcified by option `ik_sd_disable_cron`.
    """
    to_disable_ids = openerp.tools.config.options.get('ik_sd_disable_cron', None)

    if to_disable_ids:
        where = None
        # if we have in config something like '>8', we disable all crons with ID > 8
        if to_disable_ids[0] == '>':
            where = to_disable_ids
        else:
            # we have a list of ID or External IDs
            disable_ids = to_disable_ids.split(',')

            if len(disable_ids) == 0:
                _logger.error("ik_sd_disable_cron must contains a value like '>8' or like '8,5,9'")
            else:
                if disable_ids[0].isdigit():
                    # we have a list of IDS
                    where = " IN (%s)" % disable_ids
                else:
                     # we have a list of external IDS
                    where = " IN (SELECT res_id FROM ir_model_data WHERE model='ir.cron' AND name IN (%s)) " % ','.join("'{0}'".format(w) for w in disable_ids)

        if where:
            db_names = get_databases() 
            if db_names:
                for db_name in db_names:
                    try:
                        cr = get_cursor(db_name)
    
                        sql = "UPDATE ir_cron SET active=false WHERE id %s" % where
                        cr.execute(sql)
                        cr.commit()
    
                        _logger.info("Deactivated CRONs using this query: %s", sql)
                    finally:
                        cr.close()
            else:
                pass


def server_detect():

    current_ip = get_public_ip()
    
    if openerp.tools.config.options.get('ik_sd_staging_servers_ips', None):
        staging_servers_ips = openerp.tools.config.options['ik_sd_staging_servers_ips'].split(',')
    else:
        staging_servers_ips = []

    if openerp.tools.config.options.get('ik_sd_production_servers_ips', None):
        production_servers_ips = openerp.tools.config.options['ik_sd_production_servers_ips'].split(',')
    else:
        production_servers_ips = []

    if openerp.tools.config.options.get('ik_sd_email_debug_recipients', None):
        openerp.ik_sd_email_debug_recipients = openerp.tools.config.options['ik_sd_email_debug_recipients']
    else:
        openerp.ik_sd_email_debug_recipients = []

    if 'ik_sd_email_debug' in openerp.tools.config.options:
        openerp.ik_sd_email_debug = openerp.tools.config.options['ik_sd_email_debug']
    else:
        openerp.ik_sd_email_debug = True  # By default we reroute mail

    if current_ip in staging_servers_ips:
        openerp.ik_sd_is_production_server = False
        openerp.ik_sd_is_staging_server = True
        openerp.ik_sd_is_test_server = False
        openerp.ik_sd_detected_ip = current_ip
        openerp.ik_sd_server_kind = 'staging'
        _logger.info("Server is 'Staging', detected IP address=%s" % current_ip)
        update_ribbon()
        disable_crons()
        reset_passwords()
        return

    if current_ip in production_servers_ips:
        openerp.ik_sd_is_production_server = True
        openerp.ik_sd_is_staging_server = False
        openerp.ik_sd_is_test_server = False
        openerp.ik_sd_detected_ip = current_ip
        openerp.ik_sd_server_kind = 'production'
        _logger.info("Server is 'Production', detected IP address=%s" % current_ip)
        update_ribbon()
        return

    openerp.ik_sd_is_production_server = False
    openerp.ik_sd_is_staging_server = False
    openerp.ik_sd_is_test_server = True
    openerp.ik_sd_detected_ip = current_ip
    openerp.ik_sd_server_kind = 'development'
    _logger.info("Server is 'Development', detected IP address=%s" % current_ip)
    update_ribbon()
    disable_crons()
    reset_passwords()

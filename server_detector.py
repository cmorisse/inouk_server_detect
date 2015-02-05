import shutil
import os

__author__ = 'cmorisse'
import openerp
import socket
import logging

_logger = logging.getLogger('Inouk Server Detector')


def colorize_menu():
    # if we want to show visual difference between differents servers Or if we are in production server we have to force
    # the original color

    server_type = 'production'

    if openerp.tools.config.options.get('ik_sd_colorise', None):
        server_type = openerp.ik_sd_server_kind

    base_path = os.path.dirname(os.path.realpath(__file__))

    css_to_copy_file = '%s/static/src/css/server_type_style_%s.css' % (base_path, server_type)
    original_css = '%s/static/src/css/server_type_style.css' % base_path

    _logger.info(' Use CSS: %s ' % css_to_copy_file)

    shutil.copyfile(css_to_copy_file, original_css)


def server_detect():

    current_ip = socket.gethostbyname(socket.gethostname())

    #in some case, this will return 127.* so we have to use another method
    if current_ip.startswith("127."):
        current_ip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

    if openerp.tools.config.options.get('ik_sd_staging_servers_ips', None):
        staging_servers_ips = openerp.tools.config.options['ik_sd_staging_servers_ips'].split(',')
    else:
        staging_servers_ips = []

    if openerp.tools.config.options.get('ik_sd_production_servers_ips', None):
        production_servers_ips = openerp.tools.config.options['ik_sd_production_servers_ips'].split(',')
    else:
        production_servers_ips = []

    if current_ip in staging_servers_ips:
        openerp.ik_sd_is_production_server = False
        openerp.ik_sd_is_staging_server = True
        openerp.ik_sd_is_test_server = True
        openerp.ik_sd_detected_ip = current_ip
        openerp.ik_sd_server_kind = 'staging'
        _logger.info("Server is 'staging', detected IP address=%s" % current_ip)
        colorize_menu()
        return

    if current_ip in production_servers_ips:
        openerp.ik_sd_is_production_server = True
        openerp.ik_sd_is_staging_server = False
        openerp.ik_sd_is_test_server = False
        openerp.ik_sd_detected_ip = current_ip
        openerp.ik_sd_server_kind = 'production'
        _logger.info("Server is 'production', detected IP address=%s" % current_ip)
        colorize_menu()
        return

    openerp.ik_sd_is_production_server = False
    openerp.ik_sd_is_staging_server = False
    openerp.ik_sd_is_test_server = True
    openerp.ik_sd_detected_ip = current_ip
    openerp.ik_sd_server_kind = 'test'
    _logger.info("Server is 'test (or dev)', detected IP address=%s" % current_ip)
    colorize_menu()


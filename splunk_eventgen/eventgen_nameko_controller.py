from nameko.rpc import rpc
from nameko.events import EventDispatcher, event_handler, BROADCAST
from nameko.web.handlers import http
from pyrabbit.api import Client
import atexit
import ConfigParser
import logging
import os
import socket
from logger.logger_config import controller_logger_config
from logger import splunk_hec_logging_handler
import time
import json

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
EVENTGEN_ENGINE_CONF_PATH = os.path.abspath(os.path.join(FILE_PATH, "default", "eventgen_engine.conf"))

def get_hec_info_from_conf():
    hec_info = [None, None]
    config = ConfigParser.ConfigParser()
    if os.path.isfile(EVENTGEN_ENGINE_CONF_PATH):
        config.read(EVENTGEN_ENGINE_CONF_PATH)
        hec_info[0] = config.get('heclogger', 'hec_url', 1)
        hec_info[1] = config.get('heclogger', 'hec_key', 1)
    return hec_info

def exit_handler(client, hostname, logger):
    client.delete_vhost(hostname)
    logger.info("Deleted vhost {}. Shutting down.".format(hostname))

class EventgenController(object):
    name = "eventgen_controller"

    dispatch = EventDispatcher()
    PAYLOAD = 'Payload'
    logging.config.dictConfig(controller_logger_config)
    log = logging.getLogger(name)
    hec_info = get_hec_info_from_conf()
    handler = splunk_hec_logging_handler.SplunkHECHandler(targetserver=hec_info[0], hec_token=hec_info[1], eventgen_name=name)
    log.addHandler(handler)
    log.info("Logger set as eventgen_controller")
    host = socket.gethostname() + '_controller'

    server_status = {}
    server_confs = {}

    osvars, config = dict(os.environ), {}
    config["AMQP_HOST"] = osvars.get("EVENTGEN_AMQP_HOST", "localhost")
    config["AMQP_WEBPORT"] = osvars.get("EVENTGEN_AMQP_WEBPORT", 15672)
    config["AMQP_USER"] = osvars.get("EVENTGEN_AMQP_URI", "guest")
    config["AMQP_PASS"] = osvars.get("EVENTGEN_AMQP_PASS", "guest")

    pyrabbit_cl = Client('{0}:{1}'.format(config['AMQP_HOST'], config['AMQP_WEBPORT']),
                         '{0}'.format(config['AMQP_USER']),
                         '{0}'.format(config['AMQP_PASS']))
    pyrabbit_cl.create_vhost(host)
    log.info("Vhost set to {}".format(host))
    log.info("Current Vhosts are {}".format(pyrabbit_cl.get_vhost_names()))

    atexit.register(exit_handler, client=pyrabbit_cl, hostname=host, logger=log)

    ##############################################
    ################ RPC Methods #################
    ##############################################

    @event_handler("eventgen_server", "server_status", handler_type=BROADCAST, reliable_delivery=False)
    def event_handler_server_status(self, payload):
        return self.receive_status(payload)

    @event_handler("eventgen_server", "server_conf", handler_type=BROADCAST, reliable_delivery=False)
    def event_handler_server_conf(self, payload):
        return self.receive_conf(payload)

    @event_handler("eventgen_server", "server_volume", handler_type=BROADCAST, reliable_delivery=False)
    def event_handler_get_volume(self, payload):
        return self.receive_volume(payload)

    @rpc
    def index(self, target):
        try:
            if target == "all":
                self.dispatch("all_index", self.PAYLOAD)
            else:
                self.dispatch("{}_index".format(target), self.PAYLOAD)
            msg = "Index event dispatched to {}".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return '500', "Exception: {}".format(e.message)

    @rpc
    def status(self, target):
        try:
            if target == "all":
                self.dispatch("all_status", self.PAYLOAD)
            else:
                self.dispatch("{}_status".format(target), self.PAYLOAD)
            msg = "Status event dispatched to {}".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return '500', "Exception: {}".format(e.message)

    @rpc
    def start(self, target):
        try:
            if target == "all":
                self.dispatch("all_start", self.PAYLOAD)
            else:
                self.dispatch("{}_start".format(target), self.PAYLOAD)
            msg = "Start event dispatched to {}".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return '500', "Exception: {}".format(e.message)

    @rpc
    def stop(self, target):
        try:
            if target == "all":
                self.dispatch("all_stop", self.PAYLOAD)
            else:
                self.dispatch("{}_stop".format(target), self.PAYLOAD)
            msg = "Stop event dispatched to {}".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return '500', "Exception: {}".format(e.message)

    @rpc
    def restart(self, target):
        try:
            if target == "all":
                self.dispatch("all_restart", self.PAYLOAD)
            else:
                self.dispatch("{}_restart".format(target), self.PAYLOAD)
            msg = "Restart event dispatched to {}".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return '500', "Exception: {}".format(e.message)

    @rpc
    def get_conf(self, target):
        try:
            if target == "all":
                self.dispatch("all_get_conf", self.PAYLOAD)
            else:
                self.dispatch("{}_get_conf".format(target), self.PAYLOAD)
            msg = "Get_conf event dispatched to {}".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return '500', "Exception: {}".format(e.message)

    @rpc
    def set_conf(self, target, data):
        try:
            payload = data
            if target == "all":
                self.dispatch("all_set_conf", payload)
            else:
                self.dispatch("{}_set_conf".format(target), payload)
            msg = "Set_conf event dispatched to {}".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return '500', "Exception: {}".format(e.message)

    @rpc
    def edit_conf(self, target, data):
        try:
            payload = data
            if target == "all":
                self.dispatch("all_edit_conf", payload)
            else:
                self.dispatch("{}_edit_conf".format(target), payload)
            msg = "Edit_conf event dispatched to {}".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return '500', "Exception: {}".format(e.message)

    @rpc
    def bundle(self, target, data):
        try:
            data = json.loads(data)
            url = data["url"]
            self.dispatch("{}_bundle".format(target), {"url": url})
            msg = "Bundle event dispatched to {} with url {}".format(target, url)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return "500", "Exception: {}".format(e.message)
    
    @rpc
    def setup(self, target, data):
        try:
            self.dispatch("{}_setup".format(target), data)
            msg = "Setup event dispatched to {}.".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return "500", "Exception: {}".format(e.message)

    @rpc
    def get_volume(self, target):
        try:
            self.dispatch("{}_get_volume".format(target), self.PAYLOAD)
            msg = "get_volume event dispatched to {}.".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return "500", "Exception: {}".format(e.message)
    
    @rpc
    def set_volume(self, target, data):
        try:
            data = json.loads(data)
            volume = data["perDayVolume"]
            self.dispatch("{}_set_volume".format(target), {"perDayVolume": volume})
            msg = "set_volume event dispatched to {}.".format(target)
            self.log.info(msg)
            return msg
        except Exception as e:
            self.log.exception(e)
            return "500", "Exception: {}".format(e.message)

    ##############################################
    ################ HTTP Methods ################
    ##############################################

    @http('GET', '/')
    def root_page(self, request):
        self.log.info("index method called")
        home_page = '''*** Eventgen Controller ***
Host: {0}
Connected Servers: {1}
You are running Eventgen Controller.\n'''
        host = socket.gethostname()
        return home_page.format(host, self.get_current_server_vhosts())

    @http('GET', '/index')
    def http_index(self, request):
        self.index(target=self.get_target(request))
        return self.root_page(request)

    @http('GET', '/status')
    def http_status(self, request):
        self.status(target=self.get_target(request))
        return self.process_server_status()

    @http('POST', '/start')
    def http_start(self, request):
        return self.start(target=self.get_target(request))

    @http('POST', '/stop')
    def http_stop(self, request):
        return self.stop(target=self.get_target(request))

    @http('POST', '/restart')
    def http_restart(self, request):
        return self.restart(target=self.get_target(request))

    @http('GET', '/conf')
    def http_get_conf(self, request):
        self.get_conf(target=self.get_target(request))
        return self.process_server_confs()

    @http('POST', '/conf')
    def http_set_conf(self, request):
        data = request.get_data()
        if data:
            self.set_conf(target=self.get_target(request), data=data)
            return self.http_get_conf(request)
        else:
            return '400', 'Please pass valid config data.'

    @http('PUT', '/conf')
    def http_edit_conf(self, request):
        data = request.get_data()
        if data:
            self.edit_conf(target=self.get_target(request), data=data)
            return self.http_get_conf(request)
        else:
            return '400', 'Please pass valid config data.'

    @http('POST', '/bundle')
    def http_bundle(self, request):
        data = request.get_data(as_text=True)
        if data:
            return self.bundle(target=self.get_target(request), data=data)
        else:
            return "400", "Please pass in a valid object with bundle URL."

    @http('POST', '/setup')
    def http_setup(self, request):
        data = request.get_data(as_text=True)
        if data:
            return self.setup(target=self.get_target(request), data=data)
        else:
            return "400", "Please pass in a valid object with setup information."
    
    @http('GET', '/volume')
    def http_get_volume(self, request):
        self.get_volume(target=self.get_target(request))
        return self.process_server_status()

    @http('POST', '/volume')
    def http_set_volume(self, request):
        data = request.get_data(as_text=True)
        if data:
            return self.set_volume(target=self.get_target(request), data=data)
        else:
            return "400", "Please pass in a valid object with volume."

    ##############################################
    ############### Helper Methods ###############
    ##############################################

    def get_target(self, request):
        data = request.get_data()
        if data:
            data = json.loads(data)
        if 'target' in data:
            return data['target']
        else:
            return "all"

    def receive_status(self, data):
        if data['server_name'] and data['server_status']:
            self.server_status[data['server_name']] = data['server_status']

    def receive_conf(self, data):
        if data['server_name'] and data['server_conf']:
            self.server_confs[data['server_name']] = data['server_conf']

    def receive_volume(self, data):
        if data['server_name'] and data["total_volume"]:
            self.server_confs[data['server_name']] = data['total_volume']

    def process_server_status(self):
        current_server_vhosts = self.get_current_server_vhosts()
        if current_server_vhosts:
            # Try for 15 iterations to get results from current server vhosts
            for i in range(15):
                if len(self.server_status) != len(current_server_vhosts):
                    time.sleep(0.3)
                    current_server_vhosts = self.get_current_server_vhosts()
            dump_value = self.server_status
        else:
            dump_value = {}
        self.server_status = {}
        return json.dumps(dump_value, indent=4)

    def process_server_confs(self):
        current_server_vhosts = self.get_current_server_vhosts()
        if current_server_vhosts:
            # Try for 15 iterations to get results from current server vhosts
            for i in range(15):
                if len(self.server_confs) != len(current_server_vhosts):
                    time.sleep(0.3)
                    current_server_vhosts = self.get_current_server_vhosts()
            dump_value = self.server_confs
        else:
            dump_value = {}
        self.server_confs = {}
        return json.dumps(dump_value, indent=4)

    def get_current_server_vhosts(self):
        current_vhosts = self.pyrabbit_cl.get_vhost_names()
        return [name for name in current_vhosts if name != '/' and name != self.host]

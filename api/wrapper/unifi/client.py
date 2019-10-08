from pyunifi.controller import Controller as _Controller
# from middleware.settings import UNIFI_ADDRESS, UNIFI_USER, UNIFI_PASSWORD # TODO: Remove this import

# TODO: Remove these fields below
# UNIFI_ADDRESS = '192.168.1.7'
# UNIFI_USER = 'ch14346'
# UNIFI_PASSWORD = 'exZu54rMe6JV7M4Qv0EF'


class UnifiClient():
    """Unifi class to interact with the Unifi Controller"""

    def __init__(self, host_address, user, password, ssl_verify=False):
        self._unifi_controller = _Controller(
            host_address, user, password, ssl_verify=ssl_verify)

    def get_clients(self):
        return self._unifi_controller.get_clients()

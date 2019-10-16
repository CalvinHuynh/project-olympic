from pyunifi.controller import Controller as _Controller


class UnifiClient():
    """Unifi class to interact with the Unifi Controller"""
    def __init__(self, host_address, user, password, ssl_verify=False):
        self._unifi_controller = _Controller(host_address,
                                             user,
                                             password,
                                             ssl_verify=ssl_verify)

    def get_clients(self):
        return self._unifi_controller.get_clients()

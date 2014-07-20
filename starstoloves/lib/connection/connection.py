class ConnectionHelper(object):

    DISCONNECTED = 0;
    CONNECTED = 1;
    FAILED = 2;

    def is_connected(self):
        return self.get_connection_state() is self.CONNECTED


class MissingUserError(Exception):
    pass
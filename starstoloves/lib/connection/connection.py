class ConnectionHelper(object):

    DISCONNECTED = 0;
    CONNECTED = 1;
    FAILED = 2;

    def get_username(self):
        return self._get_from_connection('username')

    def is_connected(self):
        return self.get_connection_state() is self.CONNECTED

    def get_connection_state(self):
        state = self._get_from_connection('state')
        if state is not None:
            return state
        return self.DISCONNECTED

    def _get_from_connection(self, key):
        connection = self.get_connection()
        if connection:
            return getattr(connection, key)
        return None

    def disconnect(self):
        try:
            connection = self.get_connection()
            if connection:
                connection.delete()
        except:
            pass

    def get_connection(self):
        if (self.user):
            try:
                return getattr(self.user, self.connection_name)
            except self.connection_class.DoesNotExist:
                pass
        return None


class MissingUserError(Exception):
    pass
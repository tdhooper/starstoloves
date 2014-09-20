class ConnectionHelper(object):

    DISCONNECTED = 0;
    CONNECTED = 1;
    FAILED = 2;

    @property
    def username(self):
        return self._get_from_connection('username')

    @property
    def is_connected(self):
        return self.connection_state is self.CONNECTED

    @property
    def connection_state(self):
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
                return self.connection_class.objects.get(user__session_key=self.user.session_key)
            except self.connection_class.DoesNotExist:
                pass
        return None


class MissingUserError(Exception):
    pass
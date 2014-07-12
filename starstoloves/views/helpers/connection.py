class ConnectionHelper(object):

    DISCONNECTED = 0;
    CONNECTED = 1;
    FAILED = 2;

    def __init__(self, session_storage):
        self.session_storage = session_storage
        if not self._get_session_key() in session_storage:
            session_storage[self._get_session_key()] = {}

    def _get_session(self):
        return self.session_storage[self._get_session_key()]

    def _get_session_key(self):
        raise NotImplementedError('Return a session key string in the subclass')

    def _set_state(self, state):
        session = self._get_session()
        session['state'] = state

    def get_connection_state(self):
        session = self._get_session()
        return session.get('state', self.DISCONNECTED)

    def is_connected(self):
        return self.get_connection_state() is self.CONNECTED

    def disconnect(self):
        print('disc')
        self.session_storage[self._get_session_key()] = {}


class DBConnectionHelper(object):

    DISCONNECTED = 0;
    CONNECTED = 1;
    FAILED = 2;

    def is_connected(self):
        return self.get_connection_state() is self.CONNECTED

from starstoloves.lib.repository import RepositoryItem

class ConnectionHelper(RepositoryItem):

    DISCONNECTED = 0;
    CONNECTED = 1;
    FAILED = 2;

    def __init__(self, username=None, state=None, **kwargs):
        self.username = username
        if state is None:
            state = self.DISCONNECTED
        self.state = state
        super().__init__(**kwargs)

    @property
    def is_connected(self):
        return self.state is self.CONNECTED

    def disconnect(self):
        self.repository.delete(self)

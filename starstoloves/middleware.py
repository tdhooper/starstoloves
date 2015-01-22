from starstoloves.lib.user import user_repository

class SessionUser:

    def process_request(self, request):
        user = None
        request.session.save()
        session_key = request.session.session_key
        request.session_user = user_repository.from_session_key(session_key)

from django.test import TestCase

class LogInTester(TestCase):
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()  # dictionary that contain all session data. (.keys())
        # will get list with all keys. return true if exist. false if none

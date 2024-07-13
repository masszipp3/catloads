from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.crypto import constant_time_compare
from datetime import datetime

# class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
#     def _today(self):
#         # Return today's date as a datetime object
#         return datetime.now()

#     def _make_hash_value(self, user, timestamp):
#         # Ensure the timestamp is in a consistent format (e.g., timestamp is the datetime the token was generated)
#         login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
#         return f"{user.pk}{user.password}{timestamp.strftime('%Y-%m-%d %H:%M:%S')}{login_timestamp}"

#     def make_token(self, user):
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         ts_encoded = urlsafe_base64_encode(force_bytes(timestamp))
#         return f"{ts_encoded}-{self._make_hash_value(user, timestamp)}"

#     def _secret_value(self, user):
#         """
#         Generate a secret value that changes upon password or other critical user details change.
#         """
#         # This is a placeholder. You might want to include actual user details that impact token security.
#         return user.password + str(user.pk)
    
#     def check_token(self, user, token):
#         """
#         Check that a password reset token is correct for a given user.
#         """
#         # Split the token
#         try:
#             ts_b64, hash = token.split("-")
#             ts = force_str(urlsafe_base64_decode(ts_b64))
#             ts = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
#         except (ValueError, IndexError, OverflowError):
#             return False

#         # Check the timestamp is within limit (e.g., within 48 hours)
#         if (self._today() - ts).total_seconds() > 48 * 3600:
#             return False

#         hash_value = self._make_hash_value(user, ts)
#         return constant_time_compare(hash_value, hash)



#!/usr/bin/env python
import os
import sys


SECRET_KEYS = ['SECRET_KEY', 'FERNET_KEY']
BYPASS_FLAG = '--dangerous'


class SecretKeyError(Exception):

    def __str__(self):
        return 'Some or all confidential env variables not found. Ensure vars: {} are set.' \
               'To bypass this check and proceed with common keys, provide flag: {}'.format(SECRET_KEYS, BYPASS_FLAG)


def validate_secret_keys_set():
    """
    Don't allow a user to run the app without the appropriate keys set as env vars, unless explicitly bypassing.
    Raises ImportError if all secret keys are not present and the bypass flag isn't deliberately provided.
    """

    # Only perform this check on the runserver command.
    if 'runserver' not in sys.argv:
        return

    sensitive_vars_set = all(os.environ.get(secret_key) for secret_key in SECRET_KEYS)

    if BYPASS_FLAG in sys.argv:
        sys.argv.remove(BYPASS_FLAG)

        no_reload = '--noreload'
        if no_reload not in sys.argv:
            sys.argv.append(no_reload)

    elif not sensitive_vars_set:
        raise SecretKeyError()


if __name__ == '__main__':

    # Ensure we're not running the server with publicly facing secrets.
    validate_secret_keys_set()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secure_drop.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

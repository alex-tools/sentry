"""
sentry.interfaces.user
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

__all__ = ('User',)

from sentry.interfaces.base import Interface
from sentry.utils.safe import trim, trim_dict
from sentry.web.helpers import render_to_string


def validate_ip(value, required=True):
    # TODO(dcramer): we should just use ipaddr here
    if not required and not value:
        return

    assert value.count('.') == 3
    for comp in value.split('.'):
        assert comp.isdigit()
        assert -1 < int(comp) <= 256
    return value


class User(Interface):
    """
    An interface which describes the authenticated User for a request.

    You should provide **at least** either an `id` (a unique identifier for
    an authenticated user) or `ip_address` (their IP address).

    All other data is.

    >>> {
    >>>     "id": "unique_id",
    >>>     "username": "my_user",
    >>>     "email": "foo@example.com"
    >>>     "ip_address": "127.0.0.1"
    >>> }
    """
    @classmethod
    def to_python(cls, data):
        data = data.copy()

        kwargs = {
            'id': trim(data.pop('id', None), 128),
            'email': trim(data.pop('email', None), 128),
            'username': trim(data.pop('username', None), 128),
            'ip_address': validate_ip(data.pop('ip_address', None), False),
        }
        kwargs['data'] = trim_dict(data.pop('data', data))
        return cls(**kwargs)

    def get_hash(self):
        return []

    def to_html(self, event, is_public=False, **kwargs):
        if is_public:
            return ''
        return render_to_string('sentry/partial/interfaces/user.html', {
            'is_public': is_public,
            'event': event,
            'user_ip_address': self.ip_address,
            'user_id': self.id,
            'user_username': self.username,
            'user_email': self.email,
            'user_data': self.data,
        })

import logging

from aiohttp_security.abc import AbstractAuthorizationPolicy


class AuthorizationPolicy(AbstractAuthorizationPolicy):

    def __init__(self, users=None):
        super().__init__()
        self.users = users

    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        return identity

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """
        return not context['users'] or identity in context['users']

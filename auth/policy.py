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
        logging.error(identity)
        if identity == 'jack':
            return identity

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """
        logging.error(identity)
        logging.error(permission)
        logging.error(context)

        if not context:
            logging.info("No context passed.")

        if identity not in context['users']:
            raise ValueError("Invalid user '%s'." % identity)
        return identity == 'jack' and permission in ('listen',)

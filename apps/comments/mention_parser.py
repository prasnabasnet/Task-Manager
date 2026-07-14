import re

from django.db.models import Q

from apps.users.models import User


def parse_mentions(text):
    """Examples:
    @manager_bob  -> username match
    @bob          -> bob@example.com (email local-part) or username "bob"
    """
    if not text:
        return User.objects.none()

    handles = {h.lower() for h in re.findall(r"@(\w+)", text)}
    if not handles:
        return User.objects.none()

    query = Q()
    for handle in handles:
        query |= Q(username__iexact=handle) | Q(email__istartswith=f"{handle}@")

    return User.objects.filter(query).distinct()

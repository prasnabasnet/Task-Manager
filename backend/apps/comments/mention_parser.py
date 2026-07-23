import re

from django.db.models import Q

from apps.users.models import User


def parse_mentions(text):
    """Extract handles mentioned via @handle and find matching users.

    Examples:
    @manager_bob  -> username match
    @bob          -> bob@example.com (email local-part) or username "bob"
    @john.doe!    -> username/email "john.doe"
    """
    if not text:
        return User.objects.none()

    # Find @handle matches not preceded by alphanumeric/_/@ to avoid email addresses like user@domain.com
    raw_handles = re.findall(r"(?<![\w@])@([\w.@+-]+)", text)
    if not raw_handles:
        return User.objects.none()

    handles = set()
    for h in raw_handles:
        cleaned = h.rstrip(".,!?:;)]}")
        if cleaned:
            handles.add(cleaned.lower())

    if not handles:
        return User.objects.none()

    query = Q()
    for handle in handles:
        query |= (
            Q(username__iexact=handle)
            | Q(email__iexact=handle)
            | Q(email__istartswith=f"{handle}@")
            | Q(profile__display_name__iexact=handle)
        )

    return User.objects.filter(query).distinct()


import re

from apps.users.models import User


def parse_mentions(text):
    """
    Finds handles starting with @ (e.g. @azhar) and returns
    a queryset of matching Users based on their username.
    """
    if not text:
        return User.objects.none()

    # regex matches @ followed by word characters (letters, numbers, underscores)
    handles = re.findall(r"@(\w+)", text)

    if not handles:
        return User.objects.none()

    # Match the extracted handles against the User.username field
    return User.objects.filter(username__in=handles)

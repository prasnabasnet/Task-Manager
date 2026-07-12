import re

from apps.users.models import User


def parse_mentions(text):
    if not text:
        return User.objects.none()
    handles = re.findall(r"@(\w+)", text)
    if not handles:
        return User.objects.none()
    pattern = r"^(" + "|".join(re.escape(h) for h in handles) + r")@"
    return User.objects.filter(email__iregex=pattern)

import re
from apps.users.models import User

def parse_mentions(text):
    if not text:
        return User.objects.none()
    usernames = re.findall(r'@(\w+)', text)
    return User.objects.filter(username__in=usernames)

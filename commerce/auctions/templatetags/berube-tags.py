from datetime import datetime

from django import template
from django.contrib.humanize.templatetags import humanize
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def nt_plus(timestamp: str, format: str = ""):
    """Convert datetime to humanized format if within the past hour or no strftime is provided

    Args:
        timestamp (str): ISO format datetime string
        format (str): strftime format (default: "")
    """
    try:
        new_datetime = datetime.fromisoformat(timestamp)
        days_since = datetime.now().astimezone() - new_datetime
    except:
        return timestamp

    if days_since.seconds < 60 * 60 or not format:
        # if days_since.days == 0 or not format:
        try:
            humanized = humanize.naturaltime(new_datetime)
            return humanized.strip()
        except:
            return timestamp

    return new_datetime.strftime(format)


@register.filter(name="max")
def return_max_value(first, second):
    if not first or not second or not type(first) == type(second):
        return None

    return max(first, second)


@register.filter
@stringfilter
def space_safe(words: str):
    return words.replace(" ", "_")

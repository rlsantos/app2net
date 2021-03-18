from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.db.models import TextChoices


class Units(TextChoices):
    VERSION = ("Version", _("Version of Installed Software"))
    QUANTITY = ("n", _("Quantity"))
    KBPS = ("Kbps", _("Kilobits/s"))
    KB = ("KB", _('KiloBytes'))
    GHZ = ("GHz", _("GHz"))


CONVERSION_FACTORS = {
    "Mbps": 10**3,
    "Gbps": 10**6,
    "MB": 10**3,
    "GB": 10**6,
    "TB": 10**9,
}


LINK_STATUS = (
    ("ESTABLISH", _("Established")),
    ("FAILED", _("Failed")),
)

DRIVER_STATUS = (
    ("STABLE", _("Stable Version")),
    ("TESTING", _("Testing Version")),
    ("UNSTABLE", _("Unstable Version")),
    ("DEVELOPMENT", _("Development Version")),
    ("FUTURE", _("Future Version")),
)

LOGICAL_RESOURCE_STATUS = (
    ("ACTIVE", _("Active")),
    ("FAILED", _("Failed")),
)

DEVICE_STATUS = (
    ("ACTIVE", _("Active")),
    ("FAILED", _("Failed")),
)

MESSAGE_TITLES = {
    "INFO": _("It just a information..."),
    "WARNING": _("One moment, We need your attention!"),
    "SUCCESS": _("Success!!!"),
    "ERROR": _("Oooppss.. An error occurred"),
}

MESSAGE_ICONS = {
    "INFO": mark_safe('<i class="fa fa-bell swing animated" style="color:blue"></i>'),
    "WARNING": mark_safe('<i class="fa fa-warning fadeInLeft animated" style="color:orange"></i>'),
    "SUCCESS": mark_safe('<i class="fa fa-check bounce animated" style="color:green"></i>'),
    "ERROR": mark_safe('<i class="fa fa-bug shake animated" style="color:red"></i>'),
}

ERROR_CSS_CLASS = 'state-error'
REQUIRED_CSS_CLASS = ''

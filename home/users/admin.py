import logging
import re

from django.contrib import admin
from django.contrib.gis.geoip2 import HAS_GEOIP2
from django.utils import timezone

from .models import Avatar, Config, Session

logger = logging.getLogger("board")

_geoip = None


def geoip():
    global _geoip
    if _geoip is None:
        if HAS_GEOIP2:
            from django.contrib.gis.geoip2 import GeoIP2

            try:
                _geoip = GeoIP2()
            except Exception as e:
                logger.warning(e)
    return _geoip


BROWSERS = (
    (re.compile("SmartHome"), "Smart Home"),
    (re.compile("Edg"), "Edge"),
    (re.compile("OPR"), "Opera"),
    (re.compile("Chrome"), "Chrome"),
    (re.compile("Safari"), "Safari"),
    (re.compile("Firefox"), "Firefox"),
    (re.compile("IE"), "Internet Explorer"),
)
DEVICES = (
    (re.compile("Windows Mobile"), "Windows Mobile"),
    (re.compile("Android"), "Android"),
    (re.compile("Linux"), "Linux"),
    (re.compile("iPhone"), "iPhone"),
    (re.compile("iPad"), "iPad"),
    (re.compile("Mac OS X 10[._]9"), "OS X Mavericks"),
    (re.compile("Mac OS X 10[._]10"), "OS X Yosemite"),
    (re.compile("Mac OS X 10[._]11"), "OS X El Capitan"),
    (re.compile("Mac OS X 10[._]12"), "macOS Sierra"),
    (re.compile("Mac OS X 10[._]13"), "macOS High Sierra"),
    (re.compile("Mac OS X 10[._]14"), "macOS Mojave"),
    (re.compile("Mac OS X 10[._]15"), "macOS Catalina"),
    (re.compile("Mac OS X"), "macOS"),
    (re.compile("NT 5.1"), "Windows XP"),
    (re.compile("NT 6.0"), "Windows Vista"),
    (re.compile("NT 6.1"), "Windows 7"),
    (re.compile("NT 6.2"), "Windows 8"),
    (re.compile("NT 6.3"), "Windows 8.1"),
    (re.compile("NT 10.0"), "Windows 10"),
    (re.compile("Windows"), "Windows"),
)


def parse_device(value):
    """
    Transform a User Agent into human readable text.
    Example output:
    * Safari on iPhone
    * Chrome on Windows 8.1
    * Safari on macOS
    * Firefox
    * Linux
    * None
    """

    browser = None
    for regex, name in BROWSERS:
        if regex.search(value):
            browser = name
            break

    device = None
    for regex, name in DEVICES:
        if regex.search(value):
            device = name
            break

    if browser and device:
        return f"{browser} on {device}"

    if browser:
        return browser

    if device:
        return device

    return None


def parse_location(value):
    """
    Transform an IP address into an approximate location.
    Example output:
    * Zwolle, The Netherlands
    * The Netherlands
    * None
    """
    try:
        location = geoip() and geoip().city(value)  # type: ignore
    except Exception:
        try:
            location = geoip() and geoip().country(value)  # type: ignore
        except Exception:
            location = None
    if location and location["country_name"]:
        if location.get("city"):
            return "{}, {}".format(location["city"], location["country_name"])
        return location["country_name"]
    return None


class ExpiredFilter(admin.SimpleListFilter):
    title = "有效的"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (("1", "有效"), ("0", "失效"))

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(expire_date__gt=timezone.now())
        elif self.value() == "0":
            return queryset.filter(expire_date__lte=timezone.now())


class OwnerFilter(admin.SimpleListFilter):
    title = "从属"
    parameter_name = "owner"

    def lookups(self, request, model_admin):
        return (("my", "我"),)

    def queryset(self, request, queryset):
        if self.value() == "my":
            return queryset.filter(user=request.user)


class SessionAdmin(admin.ModelAdmin):
    list_display = ("ip", "user", "is_valid", "last_activity", "location", "device")
    exclude = ("session_key",)
    list_filter = (ExpiredFilter, OwnerFilter)

    @admin.display(boolean=True, description="有效的")
    def is_valid(self, obj):
        return obj.expire_date > timezone.now()

    @admin.display(description="位置")
    def location(self, obj):
        return parse_location(obj.ip)

    @admin.display(description="设备")
    def device(self, obj):
        return parse_device(obj.user_agent) if obj.user_agent else ""


class AvatarAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar")


class ConfigAdmin(admin.ModelAdmin):
    list_display = ("user", "key", "value")


admin.site.register(Session, SessionAdmin)
admin.site.register(Avatar, AvatarAdmin)
admin.site.register(Config, ConfigAdmin)

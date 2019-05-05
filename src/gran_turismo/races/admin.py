from django.contrib import admin

from . import models


class ResultAdmin(admin.ModelAdmin):
    model = models.RacingResult
    list_display = readonly_fields = (
        "session",
        "url",
        "status_code",
    )
    ordering = ["-session__id", "-status_code", "url"]
    list_filter = ("session__base_url", "status_code")
    list_display_links = None


class SessionAdmin(admin.ModelAdmin):
    list_display = readonly_fields = (
        "id",
        "base_url",
        "starting_time",
        "ending_time",
        "successes",
        "redirects",
        "soft_errors",
        "hard_errors",
        "crawled",
    )
    list_display_links = None
    ordering = ['base_url', '-ending_time']

admin.site.register(models.RacingResult, ResultAdmin)
admin.site.register(models.RacingSession, SessionAdmin)

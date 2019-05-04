from django.contrib import admin

from . import models


class ResultInLine(admin.TabularInline):
    model = models.RacingResult
    readonly_fields = (
        "session",
        "url",
        "status_code",
    )
    ordering = ["-status_code", "url"]
    extra = 0

    def has_add_permission(self, request):
        return False

class SessionAdmin(admin.ModelAdmin):
    inlines = [ResultInLine,]
    list_display = readonly_fields = (
        "id",
        "starting_time",
        "ending_time",
        "successes",
        "redirects",
        "soft_errors",
        "hard_errors",
        "crawled",
    )


admin.site.register(models.RacingSession, SessionAdmin)

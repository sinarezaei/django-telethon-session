from django.contrib import admin

from django_telethon_session.models import TelethonSentFile, TelethonEntity, TelethonSession, TelethonUpdateState

admin.site.register(TelethonSession)
admin.site.register(TelethonEntity)
admin.site.register(TelethonSentFile)
admin.site.register(TelethonUpdateState)

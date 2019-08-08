from django.contrib import admin

from dropper.models import Drop


class DropAdmin(admin.ModelAdmin):

    list_display = ('id', 'text', 'last_retrieved_on', 'created_on', 'updated_on')


admin.site.register(Drop, DropAdmin)

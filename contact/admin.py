from django.contrib import admin

import contact.models as models


class ContactAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nom',
        'sujet',
        'email',
        'message',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'nom',
        'sujet',
        'email',
        'message',
    )


class NewsLetterAdmin(admin.ModelAdmin):

    list_display = ('id', 'email', 'date_add', 'date_update', 'status')
    list_filter = ('date_add', 'date_update', 'status', 'id', 'email')


def _register(model, admin_class):
    admin.site.register(model, admin_class)


_register(models.Contact, ContactAdmin)
_register(models.NewsLetter, NewsLetterAdmin)
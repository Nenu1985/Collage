from django.contrib import admin
from .models import PhotoSize, Collage


# Register your models here.
# class PhotoSizeInline(admin.TabularInline): # табулированно-табличная форма
# #class ChoiceInline(admin.StackedInline):  # списочно-стековая форма
#     model = PhotoSize



#class CollageAdmin(admin.ModelAdmin):
    #fields = ['pub_date', 'question_text']

    # fieldsets = [
    #         ('Photo Number', {'fields': ['photo_number']}),
    #         ('Cols number', {'fields': ['cols_number']}),
    #         ('Date information', {'fields': ['create_date'], 'classes': ['collapse']}),
    #     ]
    #inlines = [PhotoSize]
    # list_display = ('photo_number', 'create_date', 'was_published_recently')
    # list_filter = ['create_date']

#
# @admin.register(Collage)
# class CollageAdmin(admin.ModelAdmin):
#     fields = [
#         #'create_date',
#
#     ]

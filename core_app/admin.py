from django.contrib import admin
from core_app.models import ExtractedImage, TemporaryImage, TemporaryPDF, TemporaryPDFImage, Pdf

# Register your models here.
admin.site.register(ExtractedImage)
admin.site.register(Pdf)
admin.site.register(TemporaryImage)
admin.site.register(TemporaryPDFImage)
admin.site.register(TemporaryPDF)


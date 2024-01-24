from django.db import models

# Create your models here.


class Pdf(models.Model):
    pdf_name = models.CharField(default=None, max_length=90)
    pdf_file = models.FileField(default=None, upload_to="pdf_files/")
    images_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.pdf_name}"


class ExtractedImage(models.Model):
    pdf = models.ForeignKey(Pdf, on_delete=models.CASCADE, default=None)
    image_name = models.CharField(default=None, max_length=80)
    p_hash = models.CharField(default=None, max_length=32)
    color_feature_vector = models.CharField(default=[], max_length=2000)
    image = models.ImageField(default=None, upload_to="db_images/")

    def __str__(self):
        return f"{self.pdf} : {self.image_name}"


class TemporaryImage(models.Model):
    user_name = models.CharField(max_length=40)
    image = models.ImageField(default=None, upload_to="temporary_images/")

    def __str__(self):
        return f"{self.user_name}"


class TemporaryPDFImage(models.Model):
    user_name = models.CharField(max_length=40)
    image = models.ImageField(default=None, upload_to="temporary_pdf_images/")

    def __str__(self):
        return f"{self.user_name}"


class TemporaryPDF(models.Model):
    user_name = models.CharField(max_length=40)
    pdf_file = models.FileField(default=None, upload_to="temporary_pdf_files/")

    def __str__(self):
        return f"{self.user_name}"

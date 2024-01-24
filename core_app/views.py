import os

import cv2
import numpy as np
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from main.wsgi import *
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from core_app.hash_methods import p_hash, calculate_hamming_distance, calculate_feature_vector, \
    calculate_cosine_similarity
from core_app.models import ExtractedImage, TemporaryImage, TemporaryPDF, TemporaryPDFImage, Pdf
from main.settings import BASE_DIR
import fitz
from core_app.extraction import extrac_images_from_pdf
from django.core.files.images import ImageFile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'base.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.warning(request, "LOGIN ERROR")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('index')


@login_required(login_url="login")
def image_detection(request):
    if request.method == 'POST' and request.FILES['uploaded_file']:
        try:
            uploaded_file = request.FILES['uploaded_file']
            file_extension = uploaded_file.name.split(".")[len(uploaded_file.name.split('.')) - 1]

            if file_extension == "png" or file_extension == "jpg":
                extracted_images = ExtractedImage.objects.all()

                try:
                    user_image = TemporaryImage.objects.get(user_name=request.user)
                    if user_image:
                        if os.path.exists(user_image.image.path):
                            os.remove(user_image.image.path)
                        user_image.image = uploaded_file
                        user_image.save()
                except ObjectDoesNotExist as e:
                    user_image = TemporaryImage(user_name=request.user, image=uploaded_file)
                    user_image.save()

                image_phash = p_hash(user_image.image.path)
                most_similar_image_url = None
                most_similar_image_source = None
                most_similar_image_hamming_distance = 64

                for extracted_img in extracted_images:
                    if extracted_img.p_hash != '0':
                        hamming_dst = calculate_hamming_distance(image_phash, extracted_img.p_hash)
                        if hamming_dst != -1:
                            if hamming_dst <= most_similar_image_hamming_distance:
                                most_similar_image_url = extracted_img.image.url
                                most_similar_image_source = extracted_img.pdf.pdf_file.url
                                most_similar_image_hamming_distance = hamming_dst

                if most_similar_image_hamming_distance > 5:
                    image_color_feature = calculate_feature_vector(user_image.image.path)
                    highest_cosine_similarity = 0

                    for extracted_img in extracted_images:
                        if extracted_img.color_feature_vector != '[]':
                            most_similar_image_color_feature = np.fromstring(
                                extracted_img.color_feature_vector[1:len(extracted_img.color_feature_vector) - 1], sep=' ')
                            cosine_similarity = calculate_cosine_similarity(image_color_feature,
                                                                            most_similar_image_color_feature)
                            if cosine_similarity > highest_cosine_similarity:
                                most_similar_image_url = extracted_img.image.url
                                most_similar_image_source = extracted_img.pdf.pdf_file.url
                                highest_cosine_similarity = cosine_similarity

                return render(request, 'image_detection.html',
                              {'uploaded_image_url': user_image.image.url,
                               'most_similar_image_url': most_similar_image_url, 'most_similar_image_source': most_similar_image_source})
            else:
                messages.warning(request, "Choose file with .png or .jpg extension")
                return render(request, 'image_detection.html')

        except Exception as e:
            messages.warning(request, "Something went wrong")
            return render(request, 'image_detection.html')
    else:
        return render(request, 'image_detection.html')


@login_required(login_url="login")
def pdf_detection(request):
    if request.method == 'POST' and request.FILES['uploaded_file']:
        try:
            output_urls = []
            uploaded_file = request.FILES['uploaded_file']
            file_extension = uploaded_file.name.split(".")[len(uploaded_file.name.split('.')) - 1]
            if file_extension == "pdf":

                try:
                    user_pdf = TemporaryPDF.objects.get(user_name=request.user)
                    if user_pdf:
                        if os.path.exists(user_pdf.pdf_file.path):
                            os.remove(user_pdf.pdf_file.path)
                        user_pdf.pdf_file = uploaded_file
                        user_pdf.save()
                except ObjectDoesNotExist as e:
                    user_pdf = TemporaryPDF(user_name=request.user, pdf_file=uploaded_file)
                    user_pdf.save()

                pdf_images_list = extrac_images_from_pdf(user_pdf.pdf_file.path)

                if 0 < len(pdf_images_list) < 25:
                    extracted_images = ExtractedImage.objects.all()

                    try:
                        users_temporary_pdf_images = TemporaryPDFImage.objects.filter(user_name=request.user)
                        for img in users_temporary_pdf_images:
                            if os.path.exists(img.image.path):
                                os.remove(img.image.path)
                            img.delete()
                    except ObjectDoesNotExist as e:
                        pass

                    for img_index, pdf_image in enumerate(pdf_images_list, start=1):
                        image = ImageFile(pdf_image, f'{request.user}_{img_index}.png')
                        pdf_img_tmp = TemporaryPDFImage(user_name=request.user, image=image)
                        pdf_img_tmp.save()

                        output_dict = {'pdf_image_url': pdf_img_tmp.image.url}

                        image_phash = p_hash(pdf_img_tmp.image.path)
                        most_similar_image_url = None
                        most_similar_image_source = None
                        most_similar_image_hamming_distance = 64

                        for extracted_img in extracted_images:
                            if extracted_img.p_hash != '0':
                                hamming_dst = calculate_hamming_distance(image_phash, extracted_img.p_hash)
                                if hamming_dst != -1:
                                    if hamming_dst <= most_similar_image_hamming_distance:
                                        most_similar_image_url = extracted_img.image.url
                                        most_similar_image_source = extracted_img.pdf.pdf_file.url
                                        most_similar_image_hamming_distance = hamming_dst

                        if most_similar_image_hamming_distance > 5:
                            image_color_feature = calculate_feature_vector(pdf_img_tmp.image.path)
                            highest_cosine_similarity = 0

                            for extracted_img in extracted_images:
                                if extracted_img.color_feature_vector != '[]':
                                    most_similar_image_color_feature = np.fromstring(
                                        extracted_img.color_feature_vector[1:len(extracted_img.color_feature_vector) - 1],
                                        sep=' ')
                                    cosine_similarity = calculate_cosine_similarity(image_color_feature,
                                                                                    most_similar_image_color_feature)
                                    if cosine_similarity > highest_cosine_similarity:
                                        most_similar_image_url = extracted_img.image.url
                                        most_similar_image_source = extracted_img.pdf.pdf_file.url
                                        highest_cosine_similarity = cosine_similarity

                        output_dict['most_similar_image_url'] = most_similar_image_url
                        output_dict['most_similar_image_source'] = most_similar_image_source
                        output_urls.append(output_dict)
                    return render(request, 'pdf_detection.html', {'output_urls': output_urls})
                else:
                    messages.warning(request, "Your PDF file should have more than 0 and less than 25 images")
                    return render(request, 'pdf_detection.html')
            else:
                messages.warning(request, "Choose file with .pdf extension")
                return render(request, 'pdf_detection.html')

        except Exception as e:
            messages.warning(request, "Something went wrong")
            return render(request, 'pdf_detection.html')
    return render(request, 'pdf_detection.html')


@login_required(login_url="login")
def db_addition(request):
    if request.method == 'POST' and request.FILES['uploaded_file']:
        try:
            uploaded_file = request.FILES['uploaded_file']
            file_extension = uploaded_file.name.split(".")[len(uploaded_file.name.split('.')) - 1]
            if file_extension == "pdf":
                pdf = Pdf(pdf_name=uploaded_file.name[:-4], pdf_file=uploaded_file)
                pdf.save()
                pdf_images_list = extrac_images_from_pdf(pdf.pdf_file.path)

                extracted_images_urls = []

                if 0 < len(pdf_images_list) < 25:
                    for img_index, pdf_image in enumerate(pdf_images_list, start=1):
                        image = ImageFile(pdf_image, f'{pdf.pdf_name}_{img_index}.png')
                        pdf_img = ExtractedImage(pdf=pdf, image_name=f"{pdf.pdf_name}_{img_index}", p_hash=0, image=image)
                        pdf_img.save()
                        image_phash = p_hash(pdf_img.image.path)
                        image_color_feature_vector = calculate_feature_vector(pdf_img.image.path)
                        pdf_img.p_hash = image_phash
                        pdf_img.color_feature_vector = image_color_feature_vector
                        pdf_img.save()
                        extracted_images_urls.append(pdf_img.image.url)

                    return render(request, 'database_addition.html', {'output_urls': extracted_images_urls})
                else:
                    pdf.delete()
                    messages.warning(request, "Your PDF file should have more than 0 and less than 25 images")
                    return render(request, 'database_addition.html')
            else:
                messages.warning(request, "Choose file with .pdf extension")
                return render(request, 'database_addition.html')
        except Exception as e:
            messages.warning(request, "Something went wrong")
    return render(request, 'database_addition.html')

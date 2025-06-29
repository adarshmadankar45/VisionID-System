from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from .models import *
import face_recognition
from django.http import JsonResponse, HttpResponse
import numpy as np
from PIL import Image
import tempfile
import os
import cv2
from django.core.files import File
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse



def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login/login.html', {'form': form})


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


@login_required
def add_criminal(request):
    if request.method == 'POST':
        form = CriminalForm(request.POST, request.FILES)
        if form.is_valid():
            criminal = form.save(commit=False)
            criminal.age = calculate_age(criminal.dob)
            criminal.save()

            files = request.FILES.getlist('images')
            for f in files:
                CriminalImage.objects.create(criminal=criminal, image=f)

            return redirect('search_criminal')
    else:
        form = CriminalForm()

    return render(request, 'criminaldata/create_criminal.html', {'form': form})

@login_required
def search_criminal(request):
    query = request.GET.get('q', '')
    results = Criminal.objects.all()

    if query:
        results = results.filter(
            models.Q(first_name__icontains=query) |
            models.Q(middle_name__icontains=query) |
            models.Q(last_name__icontains=query)
        )

    context = {
        'results': results,
        'query': query
    }
    return render(request, 'criminaldata/search_criminal.html', context)

@login_required
def criminal_detail(request, criminal_id):
    criminal = get_object_or_404(Criminal, pk=criminal_id)
    images = criminal.images.all()

    context = {
        'criminal': criminal,
        'images': images
    }
    return render(request, 'criminaldata/criminal_detail.html', context)

@login_required
def dashboard(request):
    matches = []

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_files = request.FILES.getlist('images')

            for uploaded_file in uploaded_files:
                try:
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                        for chunk in uploaded_file.chunks():
                            tmp_file.write(chunk)
                        tmp_path = tmp_file.name

                    img = Image.open(tmp_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                        img.save(tmp_path)

                    match_results = compare_faces_with_database(tmp_path)

                    matches.append({
                        'tmp_image_path': tmp_path,
                        'uploaded_image': f"data:image/jpeg;base64,{image_to_base64(tmp_path)}",
                        'matches': match_results if match_results else None
                    })
                except Exception as e:
                    print(f"Error processing {uploaded_file.name}: {str(e)}")
                    continue
    else:
        form = ImageUploadForm()

    return render(request, 'login/dashboard.html', {
        'form': form,
        'matches': matches
    })


def image_to_base64(image_path):
    from base64 import b64encode
    with open(image_path, "rb") as image_file:
        return b64encode(image_file.read()).decode('utf-8')


def compare_faces_with_database(uploaded_image_path):
    try:
        uploaded_image = face_recognition.load_image_file(uploaded_image_path)
        uploaded_encodings = face_recognition.face_encodings(uploaded_image)

        if not uploaded_encodings:
            return []

        uploaded_encoding = uploaded_encodings[0]
    except Exception as e:
        print(f"Error processing uploaded image: {str(e)}")
        return []

    matches = []

    criminal_images = CriminalImage.objects.select_related('criminal').all()

    for criminal_image in criminal_images:
        try:
            known_image_path = criminal_image.image.path
            known_image = face_recognition.load_image_file(known_image_path)
            known_encodings = face_recognition.face_encodings(known_image)

            if not known_encodings:
                continue

            known_encoding = known_encodings[0]

            results = face_recognition.compare_faces([known_encoding], uploaded_encoding)
            face_distance = face_recognition.face_distance([known_encoding], uploaded_encoding)
            confidence = (1 - face_distance[0]) * 100

            if results[0] and confidence > 65:
                matches.append({
                    'criminal': criminal_image.criminal,
                    'confidence': round(confidence, 2),
                    'image_path': criminal_image.image.url,
                    'criminal_image_id': criminal_image.id
                })
        except Exception as e:
            print(f"Error processing criminal image {criminal_image.image.path}: {str(e)}")
            continue

    return sorted(matches, key=lambda x: x['confidence'], reverse=True)

def get_searched_image(request):
    if 'searched_image' in request.session:
        image_data = request.session['searched_image']['content']
        return HttpResponse(image_data, content_type='image/jpeg')
    return HttpResponse(status=404)


@login_required
def add_image_to_criminal(request):
    if request.method == 'POST':
        try:
            criminal_id = request.POST.get('criminal_id')
            searched_image = request.FILES.get('searched_image')

            if not criminal_id:
                return JsonResponse({'status': 'error', 'message': 'Criminal ID is missing'}, status=400)
            if not searched_image:
                return JsonResponse({'status': 'error', 'message': 'No image file provided'}, status=400)

            criminal = get_object_or_404(Criminal, pk=criminal_id)

            CriminalImage.objects.create(
                criminal=criminal,
                image=searched_image
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Image added to criminal record successfully'
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def preprocess_image(image_file):
    """Convert any image to RGB numpy array"""
    try:
        img = Image.open(image_file)
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        return img_array
    except Exception as e:
        raise ValueError(f"Image processing failed: {str(e)}")


def criminal_image_search(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        criminal_id = request.POST.get('add_criminal_id')
        if criminal_id and 'searched_images' in request.session:
            try:
                criminal = get_object_or_404(Criminal, pk=criminal_id)
                for img_path in request.session['searched_images']:
                    with open(img_path, 'rb') as img_file:
                        CriminalImage.objects.create(
                            criminal=criminal,
                            image=File(img_file, name=os.path.basename(img_path))
                        )
                    os.remove(img_path)
                del request.session['searched_images']
                return JsonResponse({'status': 'success', 'message': 'Images added successfully!'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    form = CriminalImageSearchForm(request.POST or None, request.FILES or None)
    results = []

    if request.method == 'POST' and form.is_valid():
        if 'searched_images' in request.session:
            for img_path in request.session['searched_images']:
                try:
                    os.remove(img_path)
                except:
                    pass

        uploaded_files = request.FILES.getlist('image')
        temp_files = []

        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                temp_files.append(tmp_file.name)

        request.session['searched_images'] = temp_files

        try:
            all_matches = []
            for img_path in temp_files:
                with open(img_path, 'rb') as img_file:
                    uploaded_img = preprocess_image(img_file)
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    gray_uploaded = cv2.cvtColor(uploaded_img, cv2.COLOR_BGR2GRAY)
                    faces_uploaded = face_cascade.detectMultiScale(
                        gray_uploaded,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30))

                    if len(faces_uploaded) == 0:
                        continue

                    criminals = Criminal.objects.prefetch_related('images').all()
                    matches = []

                    for criminal in criminals:
                        highest_confidence = 0
                        best_image = None

                        for criminal_image in criminal.images.all():
                            try:
                                crim_img = preprocess_image(criminal_image.image)
                                gray_criminal = cv2.cvtColor(crim_img, cv2.COLOR_BGR2GRAY)
                                faces_criminal = face_cascade.detectMultiScale(
                                    gray_criminal,
                                    scaleFactor=1.1,
                                    minNeighbors=5,
                                    minSize=(30, 30))

                                if len(faces_criminal) > 0:
                                    face_size_diff = abs(faces_uploaded[0][2] - faces_criminal[0][2]) / max(
                                        faces_uploaded[0][2], faces_criminal[0][2])
                                    confidence = 100 * (1 - face_size_diff)

                                    if confidence > highest_confidence:
                                        highest_confidence = confidence
                                        best_image = criminal_image.image.url
                            except Exception as e:
                                continue

                        if highest_confidence >= 40:
                            matches.append({
                                'criminal': criminal,
                                'confidence': round(highest_confidence),
                                'image': best_image,
                                'has_image': criminal.images.exists()
                            })

                    if matches:
                        matches.sort(key=lambda x: x['confidence'], reverse=True)
                        all_matches.extend(matches)

            if all_matches:
                criminal_map = {}
                for match in all_matches:
                    criminal_id = match['criminal'].id
                    if criminal_id not in criminal_map or match['confidence'] > criminal_map[criminal_id]['confidence']:
                        criminal_map[criminal_id] = match

                results = list(criminal_map.values())
                results.sort(key=lambda x: x['confidence'], reverse=True)
            else:
                return render(request, 'login/dashboard.html', {
                    'form': form,
                    'error': 'No matching records found in any uploaded images'
                })

        except Exception as e:
            return render(request, 'login/dashboard.html', {
                'form': form,
                'error': f'Error processing images: {str(e)}'
            })

    return render(request, 'login/dashboard.html', {
        'form': form,
        'results': results,
        'search_performed': request.method == 'POST' and 'image' in request.FILES,
        'has_searched_images': 'searched_images' in request.session,
        'total_criminals': Criminal.objects.count()
    })
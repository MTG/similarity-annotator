import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Annotation, Exercise, Sound, Tier
from .forms import UploadForm, ExerciseForm
from .utils import store_tmp_file


@login_required
def exercise_list(request):
    exercises_list = Exercise.objects.all()
    context = {'exercises_list': exercises_list}
    return render(request, 'annotationapp/exercises_list.html', context)


@login_required
def sound_list(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)
    if exercise is Http404:
        context = exercise
    else:
        sounds_list = exercise.sounds.all()
        context = {'sounds_list': sounds_list, 'exercise_id': exercise_id}
    return render(request, 'annotationapp/sounds_list.html', context)


@login_required
def sound_detail(request, exercise_id, sound_id):
    sound = get_object_or_404(Sound, id=sound_id)
    context = {'sound': sound}
    return render(request, 'annotationapp/sound_detail.html', context)


@login_required
@csrf_exempt
def annotation_action(request, sound_id, tier_id):
    body_unicode = request.body.decode('utf-8')
    post_body = json.loads(body_unicode)
    action = post_body['action']
    sound = get_object_or_404(Sound, id=sound_id)
    tier = get_object_or_404(Tier, id=tier_id)

    out = {'status': 'error'}
    if action == 'remove':
        annotation_id = post_body['annotation_id']
        annotation = get_object_or_404(Annotation, id=annotation_id)
        annotation.delete()
        out = {'status': 'success'}
    else:
        name = post_body.get('name', '')
        start = post_body['startTime']
        end = post_body['endTime']
        if action == 'add':
            annotation = Annotation()
            annotation.name = name
            annotation.start_time = start
            annotation.end_time = end
            annotation.user = request.user
            annotation.sound = sound
            annotation.tier = tier
            annotation.save()
            out = {'status': 'success', 'annotation_id': annotation.id}
        elif action == 'edit':
            annotation_id = post_body['annotation_id']
            annotation = get_object_or_404(Annotation, id=annotation_id)
            annotation.name = name
            annotation.start_time = start
            annotation.end_time = end
            annotation.user = request.user
            annotation.save()
            out = {'status': 'success', 'annotation_id': annotation.id}
    return JsonResponse(out)


@login_required
def get_annotations(request, sound_id, tier_id):
    sound = get_object_or_404(Sound, id=sound_id)
    tier = get_object_or_404(Tier, id=tier_id)
    annotations = Annotation.objects.filter(sound=sound, tier=tier)
    ret = []
    for i in annotations.all():
        ret.append({
            'annotation_id': i.id,
            'startTime': i.start_time,
            'endTime': i.end_time
            })
    return JsonResponse({'status': 'success', 'annotations': ret})


@login_required
def upload(request):
    if request.method == 'POST':
        file_form = UploadForm(files=request.FILES)
        exercise_form = ExerciseForm(request.POST)
        forms = {'file': file_form, 'exercise': exercise_form}
        if file_form.is_valid() and exercise_form.is_valid():
            tmp_path = store_tmp_file(request.FILES['zip_file'])
            call_command('gm_client_unzip_sound_files', file_path=tmp_path, exercise_name=request.POST['name'])
            return redirect('exercise_list')
    else:
        forms = {'file_form': UploadForm(), 'exercise_form': ExerciseForm()}
    context = {'forms': forms}
    return render(request, 'annotationapp/upload_form.html', context)

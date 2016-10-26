from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Exercise, Sound
from django.conf import settings


@login_required
def exercise_list(request):
    exercises_list = Exercise.objects.all()
    context = {'exercises_list': exercises_list}
    return render(request, 'annotation-app/exercises_list.html', context)


def sound_list(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)
    if exercise is Http404:
        context = exercise
    else:
        sounds_list = exercise.sounds.all()
        context = {'sounds_list': sounds_list, 'exercise_id': exercise_id}
    return render(request, 'annotation-app/sounds_list.html', context)


def sound_detail(request, exercise_id, sound_id):
    sound = get_object_or_404(Sound, id=sound_id)
    context = {'sound': sound}
    return render(request, 'annotation-app/sound_detail.html', context)

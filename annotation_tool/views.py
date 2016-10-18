from django.shortcuts import render, get_object_or_404
from django.http import Http404
from models import Exercise, Sound


def exercise_list(request):
    exercises_list = Exercise.objects.all()
    context = {'exercises_list': exercises_list}
    return render(request, 'annotation_tool/exercises_list.html', context)


def sound_list(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)
    if exercise is Http404:
        context = exercise
    else:
        sounds_list = exercise.sounds.all()
        context = {'sounds_list': sounds_list, 'exercise_id': exercise_id}
    return render(request, 'annotation_tool/sounds_list.html', context)


def sound_detail(request, exercise_id, sound_id):
    sound = get_object_or_404(Sound, id=sound_id)
    context = {'sound': sound}
    return render(request, 'annotation_tool/sound_detail.html', context)

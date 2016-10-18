from django.http import HttpResponse
from django.shortcuts import render
from models import Dataset


def dataset_list(request):
    datasets_list = Dataset.objects.all()
    context = {'datasets_list': datasets_list}
    return render(request, 'annotation_tool/datasets_list.html', context)


def sound_list(request, dataset_id):
    dataset = Dataset.objects.get(id=dataset_id)
    sounds_list = dataset.sounds.all()
    context = {'sounds_list': sounds_list}
    return render(request, 'annotation_tool/sounds_list.html', context)


def sound_detail(request, dataset_id, sound_id):
    return HttpResponse("This is the annotation page for sound %s from dataset %s" % (sound_id, dataset_id))

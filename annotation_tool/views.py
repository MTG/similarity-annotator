from django.shortcuts import render, get_object_or_404
from django.http import Http404
from models import Dataset, Sound


def dataset_list(request):
    datasets_list = Dataset.objects.all()
    context = {'datasets_list': datasets_list}
    return render(request, 'annotation_tool/datasets_list.html', context)


def sound_list(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id)
    if dataset is Http404:
        context = dataset
    else:
        sounds_list = dataset.sounds.all()
        context = {'sounds_list': sounds_list}
    return render(request, 'annotation_tool/sounds_list.html', context)


def sound_detail(request, dataset_id, sound_id):
    sound = get_object_or_404(Sound, id=sound_id)
    context = {'sound': sound}
    return render(request, 'annotation_tool/sound_detail.html', context)

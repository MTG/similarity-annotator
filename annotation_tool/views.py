from django.http import HttpResponse
from django.shortcuts import render
from models import Dataset


def dataset_list(request):
    datasets_list = Dataset.objects.all()
    context = {'datasets_list': datasets_list}
    return render(request, 'annotation_tool/datasets_list.html', context)


def sound_list(request, dataset_id):
    dataset = Dataset.objects.get(id=dataset_id)
    list_of_sounds = dataset.sounds.all()
    output = ','.join([sound.filename for sound in list_of_sounds])
    return HttpResponse("List of sounds for the dataset %s: %s" % (dataset_id, output))


def sound_detail(request, sound_id):
    return HttpResponse("This is the annotation page for sound %s" % sound_id)

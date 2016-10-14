from django.http import HttpResponse
from models import Dataset


def dataset_list(request):
    list_of_datasets = Dataset.objects.all()
    output = ','.join([dataset.name for dataset in list_of_datasets])
    return HttpResponse("The list of datasets: %s" % output)


def sound_list(request, dataset_id):
    dataset = Dataset.objects.get(id=dataset_id)
    list_of_sounds = dataset.sounds.all()
    output = ','.join([sound.filename for sound in list_of_sounds])
    return HttpResponse("List of sounds for the dataset %s: %s" % (dataset_id, output))


def sound_detail(request, sound_id):
    return HttpResponse("This is the annotation page for sound %s" % sound_id)

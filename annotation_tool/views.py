from django.http import HttpResponse


def dataset_list(request):
    return HttpResponse("The list of datasets")


def sound_list(request, dataset_id):
    return HttpResponse("The list of sounds for the dataset %s" % dataset_id)


def sound_detail(request, sound_id):
    return HttpResponse("This is the annotation page for sound %s" % sound_id)

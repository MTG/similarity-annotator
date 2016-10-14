from django.http import HttpResponse


def sound_list(request):
    return HttpResponse("The list of sounds")


def sound_detail(request, sound_id):
    return HttpResponse("This is the annotation page for sound %s" % sound_id)

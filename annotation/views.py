import os
import json

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse

from .models import Exercise, Sound, Tier, DataSet, Tag
from .forms import TierForm


@login_required
def data_set_list(request):
    data_sets_list = request.user.datasets.all()
    context = {'data_sets_list': data_sets_list}
    return render(request, 'annotationapp/data_sets_list.html', context)


@login_required
def exercise_list(request, dataset_id):
    data_set = DataSet.objects.get(id=dataset_id)
    exercises_list = data_set.exercises.all().order_by('-created_at')
    context = {'exercises_list': exercises_list, 'dataset_id': dataset_id}
    return render(request, 'annotationapp/exercises_list.html', context)


@login_required
def tier_delete(request, exercise_id, tier_id):
    exercise = Exercise.objects.get(id=exercise_id)
    tier = exercise.tiers.get(id=tier_id)
    if request.method == 'POST':
        tier.delete()
        return redirect(reverse('sound_list', kwargs={
            'exercise_id': exercise_id
        }))
    context = {'exercise': exercise, 'tier': tier}
    return render(request, 'annotationapp/tier_delete.html', context)


@login_required
def tier_edit(request, exercise_id, tier_id):
    exercise = Exercise.objects.get(id=exercise_id)
    tiers_list = exercise.tiers.all()
    tier = tiers_list.get(id=tier_id)
    if request.method == 'POST':
        tier_form = TierForm(request.POST)
        if tier_form.is_valid():
            tier_name = request.POST['name']
            parent_tier_id = request.POST['parent_tier']
            if parent_tier_id:
                parent_tier = Tier.objects.get(id=parent_tier_id)
                tier.parent_tier=parent_tier

            tier.name = tier_name
            tier.exercise = exercise
            if 'point_annotations' in request.POST:
                tier.point_annotations = True
            else:
                tier.point_annotations = False
            tier.save()
            return redirect(reverse('sound_list', kwargs={
                'exercise_id': exercise_id
            }))
    else:
        tiers_list_ids = tiers_list.values_list('id')
        tier_form = TierForm(instance=tier, parent_tier_ids=tiers_list_ids)
    context = {'exercise': exercise, 'tier': tier, 'form': tier_form}
    return render(request, 'annotationapp/tier_creation.html', context)


@login_required
def tier_list(request, exercise_id, sound_id):
    exercise = Exercise.objects.get(id=exercise_id)
    tiers_list = exercise.tiers.all()
    if request.method == 'POST':
        tier_form = TierForm(request.POST)
        if tier_form.is_valid():
            tier_name = request.POST['name']
            exercise = Exercise.objects.get(id=exercise_id)
            parent_tier_id = request.POST['parent_tier']
            if parent_tier_id:
                parent_tier = Tier.objects.get(id=parent_tier_id)
                tier = Tier.objects.create(name=tier_name, exercise=exercise, parent_tier=parent_tier)
            else:
                tier = Tier.objects.create(name=tier_name, exercise=exercise)
            if 'point_annotations' in request.POST:
                tier.point_annotations = True
                tier.save()
    else:
        tiers_list_ids = tiers_list.values_list('id')
        tier_form = TierForm(parent_tier_ids=tiers_list_ids)
    sound = Sound.objects.get(id=sound_id)
    context = {'exercise': exercise, 'sound': sound, 'tiers_list': tiers_list, 'form': tier_form}
    # if the sound is the reference sound of the exercise, add a context parameter
    if sound == exercise.reference_sound:
        context['reference_sound'] = True
    return render(request, 'annotationapp/tiers_list.html', context)


@login_required
def sound_list(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)
    display_filter = request.GET.get('filter', False)
    sounds_list = exercise.sounds
    if display_filter == 'discarded':
        sounds_list = sounds_list.filter(is_discarded=True)
    else:
        sounds_list = sounds_list.filter(is_discarded=False)
    paginator = Paginator(sounds_list.all(), 20)
    page = request.GET.get('page')
    try:
        sounds = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        sounds = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        sounds = paginator.page(paginator.num_pages)
    context = {'display_filter': display_filter, 'exercise': exercise, 'sounds_list': sounds}
    if exercise is Http404:
        return render(request, exercise)
    if request.method == 'POST':
        reference_sound_id = request.POST['reference sound']
        sound = Sound.objects.get(id=reference_sound_id)
        exercise.reference_sound = sound
        exercise.save()
    else:
        if not exercise.reference_sound:
            return render(request, 'annotationapp/select_reference.html', context)
        else:
            reference_sound = exercise.reference_sound
            sounds_list = sounds_list.exclude(id=reference_sound.id)
            paginator = Paginator(sounds_list, 20)
            page = request.GET.get('page')
            try:
                sounds = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                sounds = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                sounds = paginator.page(paginator.num_pages)
            context['sounds_list'] = sounds
            if display_filter != 'discarded':
                context['reference_sound'] = reference_sound
    return render(request, 'annotationapp/sounds_list.html', context)


@login_required
def sound_detail(request, exercise_id, sound_id, tier_id):
    sound = get_object_or_404(Sound, id=sound_id)
    if request.method == 'POST':
        if sound.is_discarded:
            sound.is_discarded = False
        else:
            sound.is_discarded = True
        sound.save()
        return redirect('/' + exercise_id + '/sound_list')
    tier = get_object_or_404(Tier, id=tier_id)
    other_tiers = sound.exercise.tiers.all().exclude(id=tier_id)
    context = {'sound': sound, 'tier': tier, 'other_tiers': other_tiers, 'exercise_id': exercise_id}
    return render(request, 'annotationapp/sound_detail.html', context)


@login_required
def ref_sound_detail(request, exercise_id, sound_id, tier_id):
    if request.method == 'POST':
        tier_form = TierForm(request.POST)
        if tier_form.is_valid():
            tier_name = request.POST['name']
            exercise = Exercise.objects.get(id=exercise_id)
            Tier.objects.create(name=tier_name, exercise=exercise)
    else:
        tier_form = TierForm()

    sound = get_object_or_404(Sound, id=sound_id)

    tier = Tier.objects.get(id=tier_id)
    other_tiers = sound.exercise.tiers.all()
    context = {'form': tier_form, 'sound': sound, 'tier': tier, 'other_tiers': other_tiers, 'exercise_id': exercise_id}
    return render(request, 'annotationapp/ref_sound_annotation.html', context)


@login_required
@csrf_exempt
def annotation_action(request, sound_id, tier_id):
    sound = get_object_or_404(Sound, id=sound_id)
    tier = get_object_or_404(Tier, id=tier_id)
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        post_body = json.loads(body_unicode)

        sound.update_annotations(tier, post_body['annotations'], request.user)

        return JsonResponse({'status': 'success'})
    else:
        tags = Tag.objects.filter(tiers=tier).values_list('name', flat=True).all()
        ref_sound = sound.exercise.reference_sound
        out = {
            "task": {
                "feedback": "none",
                "visualization": "waveform",
                "similaritySegment": ["yes", "no"],
                "annotationTags": list(tags),
                "alwaysShowTags": False
            }
        }
        if request.GET.get('enable_spec', None):
            out['task']['visualization'] = "spectrogram"

        out['task']['segments_ref'] = ref_sound.get_annotations_for_tier(tier)
        out['task']['segments'] = sound.get_annotations_for_tier(tier, request.user)
        out['task']['url'] = os.path.join(settings.MEDIA_URL, sound.exercise.data_set.name, sound.exercise.name,
                                          sound.filename)
        out['task']['url_ref'] = os.path.join(settings.MEDIA_URL, sound.exercise.data_set.name, sound.exercise.name,
                                              ref_sound.filename)
        return JsonResponse(out)


@login_required
def download_annotations(request, sound_id):
    sound = get_object_or_404(Sound, id=sound_id)

    ret = sound.get_annotations_as_dict()
    return JsonResponse(ret)


@login_required
def tier_creation(request, exercise_id, sound_id):
    exercise = Exercise.objects.get(id=exercise_id)
    tiers_list = exercise.tiers.all()
    if request.method == 'POST':
        tier_form = TierForm(request.POST)
        if tier_form.is_valid():
            tier_name = request.POST['name']
            exercise = Exercise.objects.get(id=exercise_id)
            parent_tier_id = request.POST['parent_tier']
            if parent_tier_id:
                parent_tier = Tier.objects.get(id=parent_tier_id)
                tier = Tier.objects.create(name=tier_name, exercise=exercise, parent_tier=parent_tier)
            else:
                tier = Tier.objects.create(name=tier_name, exercise=exercise)
            if 'point_annotations' in request.POST:
                tier.point_annotations = True
                tier.save()
            return redirect('/' + exercise_id + '/' + sound_id + '/tiers_list')
    else:
        tiers_list_ids = tiers_list.values_list('id')
        tier_form = TierForm(parent_tier_ids=tiers_list_ids)
    context = {'form': tier_form, 'exercise': exercise, 'create': True}
    return render(request, 'annotationapp/tier_creation.html', context)


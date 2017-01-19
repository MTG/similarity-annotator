import os
import io
import json
import zipfile
import tempfile

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.core import serializers
from django.http import HttpResponse, Http404, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import AnnotationSimilarity, Annotation, Exercise, Sound, Tier, DataSet, Tag
from .forms import ExerciseForm, TierForm
from .utils import store_tmp_file, exercise_annotations_to_json


@login_required
def data_set_list(request):
    data_sets_list = DataSet.objects.all()
    context = {'data_sets_list': data_sets_list}
    return render(request, 'annotationapp/data_sets_list.html', context)


@login_required
def exercise_list(request, dataset_id):
    data_set = DataSet.objects.get(id=dataset_id)
    exercises_list = data_set.exercises.all()
    context = {'exercises_list': exercises_list, 'dataset_id':dataset_id}
    return render(request, 'annotationapp/exercises_list.html', context)


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
                Tier.objects.create(name=tier_name, exercise=exercise, parent_tier=parent_tier)
            else:
                Tier.objects.create(name=tier_name, exercise=exercise)
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
    other_tiers = sound.exercise.tiers.all()
    context = {'sound': sound, 'tier_id': tier_id, 'tier': tier, 'other_tiers': other_tiers, 'exercise_id': exercise_id}
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


def update_annotation(old_annotation, new_annotation, user):
    old_annotation.start_time = new_annotation['start']
    old_annotation.end_time = new_annotation['end']
    old_annotation.name = new_annotation['annotation']
    old_annotation.user = user
    old_annotation.save()


@login_required
@csrf_exempt
def annotation_action(request, sound_id, tier_id):
    sound = get_object_or_404(Sound, id=sound_id)
    tier = get_object_or_404(Tier, id=tier_id)
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        post_body = json.loads(body_unicode)
        added = {}
        old_annotations = Annotation.objects.filter(sound=sound, tier=tier)
        for a in post_body['annotations']:
            a_obj = None
            if isinstance(a['id'], int):
                a_obj = old_annotations.filter(pk=a['id'])

            if a_obj and a_obj.count():
                new_annotation = a_obj[0]
                # Update the annotatons in the parent tier and child
                related_annotations = Annotation.objects.filter(sound=sound, start_time=new_annotation.start_time,
                                                                end_time=new_annotation.end_time,
                                                                name=new_annotation.name)
                if tier.parent_tier:
                    related_annotations = related_annotations.filter(tier=tier.parent_tier).all()
                    for rel in related_annotations:
                        update_annotation(rel, a, request.user)
                for child in tier.child_tiers.all():
                    related_annotations = related_annotations.filter(tier=child).all()
                    for rel in related_annotations:
                        update_annotation(rel, a, request.user)

                # Update the annotation in the current tier
                update_annotation(new_annotation, a, request.user)
            else:
                new_annotation = Annotation.objects.create(sound=sound, start_time=a['start'], end_time=a['end'],
                                                           tier=tier, name=a['annotation'], user=request.user)
                if tier.parent_tier:
                    parent_annotation = Annotation.objects.create(sound=sound, start_time=a['start'], end_time=a['end'],
                           tier=tier.parent_tier, name=a['annotation'], user=request.user)
                for child in tier.child_tiers.all():
                    child_annotation = Annotation.objects.create(sound=sound, start_time=a['start'], end_time=a['end'],
                           tier=child, name=a['annotation'], user=request.user)

            # Re-create all AnnotationSimilarity for this user
            new_annotation.annotationsimilarity_set.filter(user=request.user).delete()
            if a['similarity'] == 'yes':
                ref = Annotation.objects.get(id=int(a['reference']))
                AnnotationSimilarity.objects.create(reference=ref, similar_sound=new_annotation,
                                                    similarity_measure=float(a['similValue']),
                                                    user=request.user)

            added[new_annotation.id] = {'start': a['start'], 'end': a['end']}

        # Remove old_annotation that are not in new list
        for a in old_annotations.all():
            if a.id not in added:
                # Delete annotation in the parent tier and child
                related_annotations = Annotation.objects.filter(sound=sound, start_time=a.start_time,
                                                                end_time=a.end_time, name=a.name)
                if tier.parent_tier:
                    related_annotations = related_annotations.filter(tier=tier.parent_tier).all()
                    for rel in related_annotations:
                        rel.delete()
                for child in tier.child_tiers.all():
                    related_annotations = related_annotations.filter(tier=child).all()
                    for rel in related_annotations:
                        rel.delete()

                # Delete annotation in the current tier
                a.delete()

        # create annotations in child tiers
        if tier.child_tiers.all():
            for child_tier in tier.child_tiers.all():
                if Annotation.objects.filter(sound=sound, tier=child_tier).count() == 0:
                    for k in added.keys():
                        Annotation.objects.create(start_time=added[k]['start'], end_time=added[k]['end'], sound=sound,
                                                  tier=child_tier, user=request.user)

        # update annotation_state of sound
        num_ref_annotations = Annotation.objects.filter(sound=sound.exercise.reference_sound, tier=tier).count()
        added_annotations = Annotation.objects.filter(sound=sound, tier=tier)
        num_similarity = AnnotationSimilarity.objects.filter(similar_sound__in=added_annotations).count()
        state = 'E'
        if num_ref_annotations == added_annotations.count():
            state = 'I'
            if num_similarity > 0:
                state = 'C'
        sound.annotation_state = state
        sound.save()

        out = {'status': 'success'}
        return JsonResponse(out)
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
        out['task']['segments_ref'] = []
        for a in Annotation.objects.filter(sound=ref_sound, tier=tier).all():
            out['task']['segments_ref'].append({
                "start": a.start_time,
                "end": a.end_time,
                "annotation": a.name,
                "id": a.id,
                })
        out['task']['segments'] = []
        for a in Annotation.objects.filter(sound=sound, tier=tier).all():
            annotation = {
                "start": a.start_time,
                "end": a.end_time,
                "annotation": a.name,
                "id": a.id,
                "similarity": 'no'
                }
            references = a.annotationsimilarity_set
            # If user is staff then we return all the AnnotationSimilarity values
            if not request.user.is_staff:
                references = references.filter(user=request.user)

            references = references.all()
            many_values = []
            for ref in references:
                many_values.append(ref.similarity_measure)

            if len(many_values) > 1:
                annotation['manyValues'] = many_values

            if len(references):
                reference = references[0]
                annotation['similarity'] = "yes"
                annotation['similValue'] = reference.similarity_measure
                annotation['reference'] = reference.reference_id

            out['task']['segments'].append(annotation)

        out['task']['url'] = os.path.join(settings.MEDIA_URL, sound.exercise.data_set.name, sound.exercise.name,
                                          sound.filename)
        out['task']['url_ref'] = os.path.join(settings.MEDIA_URL, sound.exercise.data_set.name, sound.exercise.name,
                                              ref_sound.filename)
        return JsonResponse(out)


@login_required
def get_annotations(request, sound_id, tier_id):
    sound = get_object_or_404(Sound, id=sound_id)
    tier = get_object_or_404(Tier, id=tier_id)
    annotations = Annotation.objects.filter(sound=sound, tier=tier)
    ret = []
    for i in annotations.all():
        references = i.annotationsimilarity_set.all()
        annotation = {
            'annotation_id': i.id,
            'startTime': i.start_time,
            'endTime': i.end_time,
            'name': i.name
            }
        if len(references):
            reference = references[0]
            annotation['referenceId'] = reference.reference_id
        ret.append(annotation)
    return JsonResponse({'status': 'success', 'annotations': ret})


@login_required
def download_annotations(request, sound_id):
    sound = get_object_or_404(Sound, id=sound_id)

    ret = sound.get_annotations_as_dict()
    return JsonResponse(ret)


@login_required
def upload(request, dataset_id):
    if request.method == 'POST':
        exercise_form = ExerciseForm(request.POST, files=request.FILES)
        if exercise_form.is_valid():
            exercise = exercise_form.save(commit=False)
            dataset = DataSet.objects.get(id=dataset_id)
            exercise.data_set = dataset
            exercise.save()
            exercise_name = request.POST['name']
            tmp_path = store_tmp_file(request.FILES['zip_file'], exercise_name)
            call_command('gm_client_unzip_sound_files', file_path=tmp_path, dataset_name=dataset.name,
                         exercise_name=exercise_name)
            return render(request, 'annotationapp/upload_success.html')
    else:
        exercise_form = ExerciseForm()
    context = {'form': exercise_form, 'dataset_id': dataset_id}
    return render(request, 'annotationapp/upload_form.html', context)


@login_required
def download(request, exercise_id):
    annotations_json = exercise_annotations_to_json(exercise_id)
    exercise = Exercise.objects.get(id=exercise_id)
    response = HttpResponse(annotations_json, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=' + exercise.name + '.json'
    return response

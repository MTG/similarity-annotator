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
    if display_filter != 'all':
        if display_filter != 'discarded':
            sounds_list = sounds_list.filter(annotations__isnull=True)
        else:
            sounds_list = sounds_list.filter(is_discarded=True)
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
        sound.is_discarded = True
        sound.save()
        return redirect('/' + exercise_id + '/sound_list')
    tier = get_object_or_404(Tier, id=tier_id)
    choose_next = False
    next_tier = None
    for t in sound.exercise.tiers.order_by('id').all():
        if choose_next:
            next_tier = reverse('sound_detail', kwargs={"sound_id": sound_id, "tier_id": t.id,
                                                        "exercise_id": exercise_id})
            choose_next = False
        if t.id == int(tier_id):
            choose_next = True

    context = {'next_url': next_tier, 'sound': sound, 'tier_id': tier_id, 'tier': tier}
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

    choose_next = False
    next_tier = None
    for t in sound.exercise.tiers.order_by('id').all():
        if choose_next:
            next_tier = reverse('ref_sound_detail', kwargs={"sound_id": sound_id,
                        "tier_id": t.id,
                        "exercise_id": exercise_id})
            choose_next = False
        if t.id == int(tier_id):
            choose_next = True

    context = {'next_url': next_tier, 'form': tier_form, 'sound': sound}
    context['tier_id'] = tier_id
    return render(request, 'annotationapp/ref_sound_annotation.html', context)


@login_required
@csrf_exempt
def annotation_action(request, sound_id, tier_id):
    sound = get_object_or_404(Sound, id=sound_id)
    tier = get_object_or_404(Tier, id=tier_id)
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        post_body = json.loads(body_unicode)
        Annotation.objects.filter(sound=sound, tier=tier).delete()
        for a in post_body['annotations']:
            new_annotation = Annotation.objects.create(start_time=a['start'], end_time=a['end'], name=a['annotation'],
                                                       sound=sound, tier=tier, user=request.user)
            # create annotations in child tiers
            if tier.child_tiers.all():
                for child_tier in tier.child_tiers.all():
                    Annotation.objects.create(start_time=a['start'], end_time=a['end'], sound=sound, tier=child_tier,
                                              user=request.user)
            if a['similarity'] == 'yes':
                ref = Annotation.objects.get(id=int(a['reference']))
                AnnotationSimilarity.objects.create(reference=ref, similar_sound=new_annotation,
                                                    similarity_measure=float(a['similValue']))

        out = {'status': 'success'}
        return JsonResponse(out)
    else:
        tags = Tag.objects.values_list('name', flat=True).all()
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
            references = a.annotationsimilarity_set.all()
            annotation = {
                "start": a.start_time,
                "end": a.end_time,
                "annotation": a.name,
                "id": a.id,
                "similarity": 'no'
                }
            if len(references):
                reference = references[0]
                annotation['similarity'] = "yes"
                annotation['similValue'] = reference.similarity_measure
                annotation['reference'] = reference.reference_id
            out['task']['segments'].append(annotation)

        out['task']['url'] = '%s%s' % (settings.MEDIA_URL, sound.filename)
        out['task']['url_ref'] = '%s%s' % (settings.MEDIA_URL, ref_sound.filename)
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

    s = io.BytesIO()
    zf = zipfile.ZipFile(s, "w")
    zip_subdir = "sound_%d" % sound.id
    zip_filename = "%s.zip" % zip_subdir
    for tier in sound.exercise.tiers.all():
        annotations = Annotation.objects.filter(sound=sound, tier=tier)

        ret = []
        for i in annotations.all():
            ret.append({
                'annotation_id': i.id,
                'startTime': str(i.start_time),
                'endTime': str(i.end_time)
                })
        # Generate XML version of annotations
        XMLSerializer = serializers.get_serializer("xml")
        xml_serializer = XMLSerializer()
        fp, temp_file = tempfile.mkstemp(".xml")
        print("---------------")
        print(temp_file)
        print("---------------")
        xml_serializer.serialize(annotations.all(), strem=fp)

        zip_path = os.path.join(zip_subdir, "tier_%s.xml" % tier.id)
        zf.write(temp_file, zip_path)

        # Generate JSON version of annotations
        fp, temp_file = tempfile.mkstemp(".json")
        json.dump(ret, open(temp_file, 'w'))

        zip_path = os.path.join(zip_subdir, "tier_%s.json" % tier.id)
        zf.write(temp_file, zip_path)

    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


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

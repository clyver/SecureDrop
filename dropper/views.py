from django import forms, http
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render

from dropper.models import Drop


class NewDropForm(forms.Form):

    message = forms.CharField(label='Your secret message')


def index(request):

    if request.method == 'GET':
        form = NewDropForm()
    else:
        form = NewDropForm(request.POST)

        if form.is_valid():
            drop = Drop.objects.create(text=form.cleaned_data['message'])
            return http.HttpResponse('Thanks, your link is: {}{}'.format(request.get_host(), drop.link), status=201)
        else:
            return http.HttpResponseBadRequest('Bad request: {}'.format(', '.join(form.errors)))

    return render(request, 'dropper/new-drop.html', {'form': form})


def get_drop(request, drop_uuid):
    """
    Attempt to lookup a Drop with the provided uuid.
    """

    try:
        drop = Drop.objects.get(uuid=drop_uuid)
    except (ObjectDoesNotExist, ValidationError):
        return http.HttpResponseNotFound('Sorry! Drop not found.')
    else:
        drop_retrieval = drop.attempt_retrieval()

        if drop_retrieval.was_successful:
            # TODO: A DRF Serializer might be appropriate here at some point.
            drop_fields = ['uuid', 'created_on', 'updated_on', 'text']
            drop_data = {drop_field: getattr(drop, drop_field) for drop_field in drop_fields}
            return http.JsonResponse(drop_data)
        else:
            return http.HttpResponseForbidden("Not authorized to retrieve Drop.")

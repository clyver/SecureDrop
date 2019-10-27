from django import forms, http
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render
from django.urls import reverse

from dropper.models import Drop


class NewDropForm(forms.Form):

    text = forms.CharField(label='Your secret message', widget=forms.Textarea)
    password = forms.CharField(required=False)
    retrieval_limit = forms.IntegerField(initial=1)
    rejection_limit = forms.IntegerField(required=False)
    expires_on = forms.DateField(required=False)


class DropRetrievalForm(forms.Form):
    password = forms.CharField()


def index(request):

    if request.method == 'GET':
        form = NewDropForm()
    else:
        form = NewDropForm(request.POST)

        if form.is_valid():
            drop = Drop.objects.create(**form.cleaned_data)
            return http.HttpResponse('Thanks, your link is: {}{}'.format(request.get_host(), drop.link), status=201)
        else:
            return http.HttpResponseBadRequest('Bad request: {}'.format(', '.join(form.errors)))

    return render(request, 'dropper/base-form.html', {'form': form, 'path': reverse('index')})


def attempt_to_dispense_drop(drop, password=None):

    drop_retrieval = drop.attempt_retrieval(password=password)
    if drop_retrieval.was_successful:
        # TODO: A DRF Serializer might be appropriate here at some point.
        drop_fields = ['uuid', 'created_on', 'updated_on', 'text']
        drop_data = {drop_field: getattr(drop, drop_field) for drop_field in drop_fields}
        return http.JsonResponse(drop_data)
    else:
        return http.HttpResponseForbidden("Not authorized to retrieve Drop.")


def get_drop(request, drop_uuid):
    """
    Attempt a Drop lookup with the provided uuid.
    """

    try:
        drop = Drop.objects.get(uuid=drop_uuid)
    except (ObjectDoesNotExist, ValidationError):
        return http.HttpResponseNotFound('Sorry! Drop not found.')

    if request.method == 'GET':
        if drop.password:
            # If a client is requesting this Drop and password is required, redirect them to provide a password.
            return render(
                request,
                'dropper/base-form.html',
                {
                    'form': DropRetrievalForm(),
                    'path': reverse('get_drop', kwargs={'drop_uuid': drop.uuid})
                }
            )
        else:
            return attempt_to_dispense_drop(drop)

    else:
        password = request.POST.get('password')
        return attempt_to_dispense_drop(drop, password=password)

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, Http404
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
            return HttpResponse('Thanks, your link is: {}{}'.format(request.get_host(), drop.link))

    return render(request, 'dropper/new-drop.html', {'form': form})


def get_drop(request, drop_uuid):

    try:
        drop = Drop.objects.get(uuid=drop_uuid)
    except (ObjectDoesNotExist, ValidationError):
        return Http404('Sorry! Message not found.')
    else:
        drop.mark_retrieved()
        return HttpResponse(drop.text)

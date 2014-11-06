import io

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

import apiclient.discovery
from gapi import GApi


api = GApi(client_id=settings.OAUTH2_CLIENT_ID if hasattr(settings, 'OAUTH2_CLIENT_ID') else '',
           client_secret=settings.OAUTH2_CLIENT_SECRET if hasattr(settings, 'OAUTH2_CLIENT_SECRET') else '',
           scope=settings.GOOGLE_AUTH_SCOPE if hasattr(settings, 'GOOGLE_AUTH_SCOPE') else '',
           redirect_uri=settings.OAUTH2_HOST + '/' + settings.OAUTH2_CALLBACK
           if hasattr(settings, 'OAUTH2_HOST') and hasattr(settings, 'OAUTH2_CALLBACK') else None)


@login_required(login_url='login')
@api.oauth2_required
def oauth2_begin(request):
    return HttpResponseRedirect(reverse('oauth2_complete'))
    # TODO or simply
    #return write_file(request)


@login_required(login_url='login')
@api.oauth2_redirect
def oauth2_callback(request):
    return HttpResponseRedirect(reverse('oauth2_complete'))
    # TODO or simply
    # return write_file(request)


@login_required(login_url='login')
@api.oauth2_required
def oauth2_complete(request):
    return write_file(request)


def index(request):
    return render_to_response('index.html', {}, RequestContext(request))


# ===========================================================================


def write_file(request):
    service = api.get_gservice(request, 'drive', 'v2')
    new_file = create_file(service)
    return render_to_response('result.html', {'new_file': new_file}, RequestContext(request))


def create_file(drive_service):
    # MIME_TYPE = 'application/vnd.google-apps.spreadsheet'
    mime_type = 'text/csv'
    title = 'Name of Spreadsheet'
    description = 'some description'
    file_data = io.StringIO(sample_csv)
    media_body = apiclient.http.MediaIoBaseUpload(file_data, mimetype=mime_type, resumable=False)
    body = {
        #'mimeType': mime_type,
        'title': title,
        'description': description,
    }
    new_file = drive_service.files().insert(body=body, media_body=media_body).execute()
    return new_file


sample_csv = u''.join([
    'Year,Make,Model,Description,Price',
    '1997,Ford,E350,"ac, abs, moon",3000.00',
    '1999,Chevy,"Venture ""Extended Edition""","",4900.00',
    '1999,Chevy,"Venture ""Extended Edition, Very Large""",,5000.00',
    '1996,Jeep,Grand Cherokee,"MUST SELL!'
    'air, moon roof, loaded",4799.00'
])
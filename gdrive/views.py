import io

import httplib2
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from oauth2client.django_orm import Storage
from oauth2client import xsrfutil

import apiclient.discovery

from models import CredentialsModel

#TODO
client_secrets = {
    'oauth2_client_id': settings.OAUTH2_CLIENT_ID,
    'oauth2_client_secret': settings.OAUTH2_CLIENT_SECRET,
    'google_auth_scope': settings.GOOGLE_AUTH_SCOPE,
    'oauth2_redirect_uri': settings.OAUTH2_REDIRECT_URI
}

FLOW = OAuth2WebServerFlow(
    client_secrets.get('oauth2_client_id', settings.OAUTH2_CLIENT_ID),
    client_secrets.get('oauth2_client_secret', settings.OAUTH2_CLIENT_SECRET),
    client_secrets.get('google_auth_scope', settings.GOOGLE_AUTH_SCOPE),
    client_secrets.get('oauth2_redirect_uri', settings.OAUTH2_REDIRECT_URI)
)


@login_required(login_url='/login/')
def begin(request):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid is True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        drive_service = apiclient.discovery.build("drive", "v2", http=http)
        new_file = create_file(drive_service)
        return render_to_response('result.html', {'new_file': new_file}, RequestContext(request))


@login_required(login_url='/login/')
def complete(request):
    if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], request.user):
        return HttpResponseBadRequest()
    credential = FLOW.step2_exchange(request.REQUEST)
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)
    #TODO here the redirect
    return HttpResponseRedirect("/")


def index(request):
    return render_to_response('index.html', {}, RequestContext(request))


def create_file(drive_service):
#MIME_TYPE = 'application/vnd.google-apps.spreadsheet'
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
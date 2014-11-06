from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import Storage
from oauth2client import xsrfutil
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.conf import settings
import httplib2

import apiclient.discovery
from functools import wraps

from models import CredentialsModel


class GApi(object):

    def __init__(self, client_id='', client_secret='', scope='', redirect_uri=None):
        self.flow = OAuth2WebServerFlow(client_id, client_secret, scope, redirect_uri=redirect_uri)

    def oauth2_required(self, view_function):
        @wraps(view_function)
        def wrapper(request, *args, **kwargs):
            storage = Storage(CredentialsModel, 'id', request.user, 'credential')
            credential = storage.get()
            if credential is None or credential.invalid is True:
                self.flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, request.user)
                authorize_url = self.flow.step1_get_authorize_url()
                return HttpResponseRedirect(authorize_url)
            else:
                return view_function(request, *args, **kwargs)
        return wrapper

    def oauth2_redirect(self, view_function):
        @wraps(view_function)
        def wrapper(request, *args, **kwargs):
            if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], request.user):
                return HttpResponseBadRequest()
            credential = self.flow.step2_exchange(request.REQUEST)
            storage = Storage(CredentialsModel, 'id', request.user, 'credential')
            storage.put(credential)
            return view_function(request, *args, **kwargs)
        return wrapper

    @classmethod
    def get_gservice(cls, request, api_name, version):
        storage = Storage(CredentialsModel, 'id', request.user, 'credential')
        credential = storage.get()
        http = httplib2.Http()
        http = credential.authorize(http)
        return apiclient.discovery.build(api_name, version, http=http)

from functools import wraps
import json
import base64

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import Storage
from oauth2client import xsrfutil
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.conf import settings
import httplib2

import apiclient.discovery
from models import CredentialsModel


class GApi(object):
    def __init__(self, client_id='', client_secret='', scope='', redirect_uri=None):
        self.flow = OAuth2WebServerFlow(client_id, client_secret, scope, redirect_uri=redirect_uri)

    def oauth2_required(self, view_function):
        """
        Decorator function that will initiate OAUTH2 WEB flow with google services
        :param view_function:
        :return:
        """
        @wraps(view_function)
        def wrapper(request, *args, **kwargs):
            storage = Storage(CredentialsModel, 'id', request.user, 'credential')
            credential = storage.get()
            if credential is None or credential.invalid is True:
                # no credential so we do oauth2 web auth
                state = {
                    #token to check on redirect
                    'token': xsrfutil.generate_token(settings.SECRET_KEY, request.user)
                }
                #extra params that need to be kept over the auth process
                if 'oauth2_state' in kwargs:
                    state['oauth2_state'] = kwargs['oauth2_state']
                #encode the whole stuff
                base64_state = base64.urlsafe_b64encode(json.dumps(state))
                #set the oauth2 state param
                self.flow.params['state'] = base64_state
                authorize_url = self.flow.step1_get_authorize_url()
                return HttpResponseRedirect(authorize_url)
            else:
                if 'oauth2_state' in kwargs:
                    del kwargs['oauth2_state']
                return view_function(request, *args, **kwargs)

        return wrapper

    def oauth2_redirect(self, view_function):
        """
        Decorator function to handle the redirect after the OAUTH2 WEB process
        :param view_function:
        :return:
        """
        @wraps(view_function)
        def wrapper(request, *args, **kwargs):
            # decode the oauth2 state param
            state = json.loads(base64.urlsafe_b64decode(str(request.REQUEST['state'])))
            #validate token
            if not 'token' in state or not xsrfutil.validate_token(settings.SECRET_KEY, state['token'], request.user):
                return HttpResponseBadRequest()
            #save oauth2 credential in db
            credential = self.flow.step2_exchange(request.REQUEST)
            storage = Storage(CredentialsModel, 'id', request.user, 'credential')
            storage.put(credential)
            #put oauth2_state params in kwargs
            if 'oauth2_state' in state:
                kwargs['oauth2_state'] = state['oauth2_state']
            return view_function(request, *args, **kwargs)

        return wrapper

    @classmethod
    def get_gservice(cls, request, api_name, version):
        """
        Get a google api service
        :param request: the request to check oauth credential
        :param api_name: Google api name ex 'drive'
        :param version: Google api version name ex v2''
        :return: the service object
        """
        storage = Storage(CredentialsModel, 'id', request.user, 'credential')
        credential = storage.get()
        http = httplib2.Http()
        http = credential.authorize(http)
        return apiclient.discovery.build(api_name, version, http=http)

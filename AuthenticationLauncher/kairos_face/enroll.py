import base64

import requests

import exceptions
import settings
import utils
import json

_enroll_base_url = settings.base_url + 'enroll'


def enroll_face(subject_id, gallery_name, url=None, file=None, additional_arguments={}):
   utils.validate_settings()
   utils.validate_file_and_url_presence(file, url)

   auth_headers = {
       'Content-type': 'application/json',
       'Accept': 'text/plain',
       'app_id': settings.app_id,
       'app_key': settings.app_key
   }

   payload = _build_payload(subject_id, gallery_name, url, file, additional_arguments)

   response = requests.post(_enroll_base_url, data=json.dumps(payload), headers=auth_headers)
   json_response = response.json()
   if response.status_code != 200 or 'Errors' in json_response:
       raise exceptions.ServiceRequestError(response.status_code, json_response, payload)

   return json_response


def _build_payload(subject_id, gallery_name, url, file, additional_arguments):
    if file is not None:
        image = _extract_base64_contents(file)
    else:
        image = url
    required_fields = {'image': image, 'subject_id': subject_id,
                       'gallery_name': gallery_name, 'multiple_faces': False}

    return dict(required_fields, **additional_arguments)


def _extract_base64_contents(file):
    with open(file, 'rb') as fp:
        image = base64.b64encode(fp.read()).decode('ascii')
    return image

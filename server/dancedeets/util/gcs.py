import logging
import io

from oauth2client.client import GoogleCredentials
from googleapiclient import errors
from googleapiclient import http
from googleapiclient.discovery import build

test_mode = False


class NotFoundError(Exception):
    pass


def _create_service():
    # Get the application default credentials. When running locally, these are
    # available after running `gcloud init`. When running on compute
    # engine, these are available from the environment.
    credentials = GoogleCredentials.get_application_default()

    # Construct the service object for interacting with the Cloud Storage API -
    # the 'storage' service, at version 'v1'.
    # You can browse other available api services and versions here:
    #     http://g.co/dv/api-client-library/python/apis/
    return build('storage', 'v1', credentials=credentials)


def put_object(bucket, filename, contents):
    if test_mode:
        return
    service = _create_service()

    # This is the request body as specified:
    # http://g.co/cloud/storage/docs/json_api/v1/objects/insert#request
    body = {
        'name': filename,
    }

    # Now insert them into the specified bucket as a media insertion.
    # http://g.co/dv/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.objects.html#insert
    f = io.BytesIO(contents)
    req = service.objects().insert(
        bucket=bucket,
        body=body,
        # You can also just set media_body=filename, but for the sake of
        # demonstration, pass in the more generic file handle, which could
        # very well be a StringIO or similar.
        media_body=http.MediaIoBaseUpload(f, 'application/octet-stream')
    )
    try:
        resp = req.execute()
    except errors.HttpError as e:
        if e.resp.status in [400, 404]:
            raise NotFoundError()
        raise
    return resp


def get_object(bucket, filename):
    if test_mode:
        return 'Dummy Object'

    try:
        service = _create_service()

        # Use get_media instead of get to get the actual contents of the object.
        # http://g.co/dv/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.objects.html#get_media
        req = service.objects().get_media(bucket=bucket, object=filename)

        out_file = io.BytesIO()
        downloader = http.MediaIoBaseDownload(out_file, req)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logging.info("Download {}%.".format(int(status.progress() * 100)))

        return out_file.getvalue()
    except errors.HttpError as e:
        if e.resp.status == 404:
            raise NotFoundError()
        raise


def delete_object(bucket, filename):
    if test_mode:
        return

    service = _create_service()

    try:
        req = service.objects().delete(bucket=bucket, object=filename)
        req.execute()
    except errors.HttpError:
        pass

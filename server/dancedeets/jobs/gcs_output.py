"""
Google Cloud Storage output utilities for Cloud Run Jobs.

Provides helpers for writing job output to GCS, replacing the
MapReduce GoogleCloudStorageOutputWriter.
"""

import datetime
import logging
import os
from typing import Iterable, Optional

from google.cloud import storage

logger = logging.getLogger(__name__)

DEFAULT_BUCKET = 'dancedeets-hrd.appspot.com'


class GCSOutputWriter:
    """
    Writes job output to Google Cloud Storage.

    Usage:
        with GCSOutputWriter(bucket, 'output/results.txt') as writer:
            for line in results:
                writer.write(line)
    """

    def __init__(
        self,
        bucket_name: str = DEFAULT_BUCKET,
        blob_name: Optional[str] = None,
        content_type: str = 'text/plain',
        include_task_index: bool = True,
    ):
        self.bucket_name = bucket_name
        self._blob_name = blob_name
        self.content_type = content_type
        self.include_task_index = include_task_index
        self._buffer: list = []
        self._client: Optional[storage.Client] = None

    @property
    def blob_name(self) -> str:
        """Get the blob name, optionally including task index."""
        if self._blob_name is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            job_name = os.environ.get('CLOUD_RUN_JOB', 'job')
            self._blob_name = f"jobs/{job_name}/{timestamp}/output.txt"

        if self.include_task_index:
            task_count = int(os.environ.get('CLOUD_RUN_TASK_COUNT', '1'))
            if task_count > 1:
                task_index = int(os.environ.get('CLOUD_RUN_TASK_INDEX', '0'))
                name, ext = os.path.splitext(self._blob_name)
                return f"{name}-{task_index:05d}{ext}"

        return self._blob_name

    @property
    def client(self) -> storage.Client:
        """Lazy-loaded GCS client."""
        if self._client is None:
            self._client = storage.Client()
        return self._client

    def write(self, line: str) -> None:
        """Write a line to the buffer."""
        self._buffer.append(line)

    def write_all(self, lines: Iterable[str]) -> None:
        """Write multiple lines to the buffer."""
        self._buffer.extend(lines)

    def flush(self) -> str:
        """
        Flush the buffer to GCS.

        Returns:
            GCS URI of the written file
        """
        if not self._buffer:
            logger.warning("No content to write to GCS")
            return ""

        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(self.blob_name)

        content = '\n'.join(str(line) for line in self._buffer)
        blob.upload_from_string(content, content_type=self.content_type)

        uri = f"gs://{self.bucket_name}/{self.blob_name}"
        logger.info(f"Wrote {len(self._buffer)} lines to {uri}")

        self._buffer = []
        return uri

    def __enter__(self) -> 'GCSOutputWriter':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._buffer:
            self.flush()


def write_to_gcs(
    content: str,
    bucket_name: str = DEFAULT_BUCKET,
    blob_name: Optional[str] = None,
    content_type: str = 'text/plain',
) -> str:
    """
    Convenience function to write content directly to GCS.

    Args:
        content: String content to write
        bucket_name: GCS bucket name
        blob_name: Path within the bucket
        content_type: MIME type

    Returns:
        GCS URI of the written file
    """
    writer = GCSOutputWriter(bucket_name, blob_name, content_type)
    writer.write(content)
    return writer.flush()


def read_from_gcs(
    bucket_name: str,
    blob_name: str,
) -> str:
    """
    Read content from a GCS file.

    Args:
        bucket_name: GCS bucket name
        blob_name: Path within the bucket

    Returns:
        File contents as string
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_text()


def list_gcs_blobs(
    bucket_name: str,
    prefix: str,
) -> list:
    """
    List blobs in a GCS bucket with a given prefix.

    Args:
        bucket_name: GCS bucket name
        prefix: Blob name prefix to filter by

    Returns:
        List of blob names
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name for blob in blobs]

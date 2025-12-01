"""
Base classes for Cloud Run Jobs.

This module provides the foundation for running batch jobs that replace
the legacy App Engine MapReduce functionality.

Cloud Run Jobs are containerized batch tasks that:
- Run to completion (not request-response like services)
- Support parallel execution via CLOUD_RUN_TASK_INDEX
- Can run up to 24 hours
- Support automatic retries

Usage:
    class MyJob(Job):
        def run(self, entity):
            # Process a single entity
            pass

    if __name__ == '__main__':
        runner = JobRunner(MyJob())
        runner.run_from_datastore('dancedeets.events.eventdata.DBEvent')
"""

import abc
import logging
import os
import sys
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Type

from google.cloud import datastore
from google.cloud import storage

from .metrics import JobMetrics

# Configure logging for Cloud Run Jobs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class Job(abc.ABC):
    """Base class for all Cloud Run Jobs."""

    def __init__(self):
        self.metrics = JobMetrics()
        self._gcs_client: Optional[storage.Client] = None
        self._datastore_client: Optional[datastore.Client] = None

    @property
    def gcs_client(self) -> storage.Client:
        """Lazy-loaded GCS client."""
        if self._gcs_client is None:
            self._gcs_client = storage.Client()
        return self._gcs_client

    @property
    def datastore_client(self) -> datastore.Client:
        """Lazy-loaded Datastore client."""
        if self._datastore_client is None:
            self._datastore_client = datastore.Client()
        return self._datastore_client

    @abc.abstractmethod
    def run(self, entity: Any) -> Optional[Any]:
        """
        Process a single entity.

        Args:
            entity: The entity to process (from Datastore query)

        Returns:
            Optional output to be collected (for jobs with output)
        """
        pass

    def setup(self) -> None:
        """Called once before processing entities. Override for initialization."""
        pass

    def teardown(self) -> None:
        """Called once after all entities processed. Override for cleanup."""
        pass

    def on_batch_complete(self, batch: List[Any]) -> None:
        """Called after processing a batch of entities. Override for batch operations."""
        pass


class BatchJob(Job):
    """Job that processes entities in batches instead of one at a time."""

    def __init__(self, batch_size: int = 20):
        super().__init__()
        self.batch_size = batch_size

    def run(self, entity: Any) -> Optional[Any]:
        """Not used for batch jobs - override run_batch instead."""
        raise NotImplementedError("BatchJob should override run_batch, not run")

    @abc.abstractmethod
    def run_batch(self, entities: List[Any]) -> Optional[List[Any]]:
        """
        Process a batch of entities.

        Args:
            entities: List of entities to process

        Returns:
            Optional list of outputs to be collected
        """
        pass


class JobRunner:
    """
    Runs a Job against a set of entities.

    Supports:
    - Datastore entity iteration with cursor-based pagination
    - Parallel task execution via CLOUD_RUN_TASK_INDEX
    - Output collection to GCS
    - Progress logging
    """

    def __init__(self, job: Job, project_id: Optional[str] = None):
        self.job = job
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT', 'dancedeets-hrd')
        self._datastore_client: Optional[datastore.Client] = None

        # Cloud Run Job environment variables
        self.task_index = int(os.environ.get('CLOUD_RUN_TASK_INDEX', '0'))
        self.task_count = int(os.environ.get('CLOUD_RUN_TASK_COUNT', '1'))
        self.attempt_index = int(os.environ.get('CLOUD_RUN_TASK_ATTEMPT', '0'))

        logger.info(
            f"JobRunner initialized: task {self.task_index + 1}/{self.task_count}, "
            f"attempt {self.attempt_index + 1}"
        )

    @property
    def datastore_client(self) -> datastore.Client:
        """Lazy-loaded Datastore client."""
        if self._datastore_client is None:
            self._datastore_client = datastore.Client(project=self.project_id)
        return self._datastore_client

    def run_from_datastore(
        self,
        entity_kind: str,
        filters: Optional[List[tuple]] = None,
        batch_size: int = 100,
        limit: Optional[int] = None,
    ) -> None:
        """
        Run the job against entities from Datastore.

        Args:
            entity_kind: Full entity kind path (e.g., 'dancedeets.events.eventdata.DBEvent')
            filters: Optional list of (property, operator, value) tuples
            batch_size: Number of entities to fetch per query
            limit: Optional maximum number of entities to process
        """
        filters = filters or []

        # Extract just the kind name (last part of the dotted path)
        kind_name = entity_kind.split('.')[-1]

        logger.info(f"Starting job for entity kind: {kind_name}")
        logger.info(f"Filters: {filters}")

        self.job.setup()

        try:
            processed_count = 0
            output_buffer: List[Any] = []

            for entity in self._iterate_entities(kind_name, filters, batch_size, limit):
                try:
                    if isinstance(self.job, BatchJob):
                        # Batch jobs handle their own batching in _iterate_entities_batched
                        raise NotImplementedError("Use run_from_datastore_batched for BatchJob")

                    result = self.job.run(entity)
                    if result is not None:
                        if isinstance(result, (list, tuple)):
                            output_buffer.extend(result)
                        else:
                            output_buffer.append(result)

                    processed_count += 1
                    self.job.metrics.increment('entities_processed')

                    if processed_count % 100 == 0:
                        logger.info(f"Processed {processed_count} entities")

                except Exception as e:
                    logger.error(f"Error processing entity {entity.key}: {e}")
                    self.job.metrics.increment('entities_failed')
                    # Continue processing other entities

            logger.info(f"Job complete. Processed {processed_count} entities.")
            logger.info(f"Metrics: {self.job.metrics.get_all()}")

        finally:
            self.job.teardown()

    def run_from_datastore_batched(
        self,
        entity_kind: str,
        filters: Optional[List[tuple]] = None,
        batch_size: int = 20,
        limit: Optional[int] = None,
    ) -> None:
        """
        Run a BatchJob against entities from Datastore.

        Args:
            entity_kind: Full entity kind path
            filters: Optional list of (property, operator, value) tuples
            batch_size: Number of entities per batch (overrides job.batch_size)
            limit: Optional maximum number of entities to process
        """
        if not isinstance(self.job, BatchJob):
            raise TypeError("run_from_datastore_batched requires a BatchJob")

        filters = filters or []
        kind_name = entity_kind.split('.')[-1]

        logger.info(f"Starting batch job for entity kind: {kind_name}")
        logger.info(f"Batch size: {batch_size}, Filters: {filters}")

        self.job.setup()

        try:
            processed_count = 0
            batch: List[Any] = []

            for entity in self._iterate_entities(kind_name, filters, batch_size, limit):
                batch.append(entity)

                if len(batch) >= batch_size:
                    self._process_batch(batch)
                    processed_count += len(batch)
                    batch = []

                    if processed_count % 100 == 0:
                        logger.info(f"Processed {processed_count} entities")

            # Process remaining entities
            if batch:
                self._process_batch(batch)
                processed_count += len(batch)

            logger.info(f"Batch job complete. Processed {processed_count} entities.")
            logger.info(f"Metrics: {self.job.metrics.get_all()}")

        finally:
            self.job.teardown()

    def _process_batch(self, batch: List[Any]) -> None:
        """Process a batch of entities."""
        try:
            self.job.run_batch(batch)
            self.job.metrics.increment('batches_processed')
            self.job.metrics.increment('entities_processed', len(batch))
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            self.job.metrics.increment('batches_failed')
            self.job.metrics.increment('entities_failed', len(batch))

    def _iterate_entities(
        self,
        kind: str,
        filters: List[tuple],
        batch_size: int,
        limit: Optional[int],
    ) -> Generator[Any, None, None]:
        """
        Iterate over Datastore entities with cursor-based pagination.

        For parallel Cloud Run Jobs, entities are distributed across tasks
        using modulo on the entity key.
        """
        query = self.datastore_client.query(kind=kind)

        for prop, op, value in filters:
            query.add_filter(prop, op, value)

        cursor = None
        total_fetched = 0

        while True:
            # Fetch a page of results
            query_iter = query.fetch(start_cursor=cursor, limit=batch_size)
            page = list(query_iter)

            if not page:
                break

            for entity in page:
                # For parallel execution, only process entities assigned to this task
                if self.task_count > 1:
                    # Use hash of key for distribution
                    entity_hash = hash(str(entity.key))
                    if entity_hash % self.task_count != self.task_index:
                        continue

                yield entity
                total_fetched += 1

                if limit and total_fetched >= limit:
                    return

            # Get cursor for next page
            cursor = query_iter.next_page_token
            if cursor is None:
                break

    def write_output_to_gcs(
        self,
        output_lines: Iterable[str],
        bucket_name: str,
        blob_name: str,
        content_type: str = 'text/plain',
    ) -> str:
        """
        Write output lines to Google Cloud Storage.

        Args:
            output_lines: Iterable of strings to write
            bucket_name: GCS bucket name
            blob_name: Path within the bucket
            content_type: MIME type of the output

        Returns:
            GCS URI of the written file
        """
        gcs_client = storage.Client()
        bucket = gcs_client.bucket(bucket_name)

        # Include task index in filename for parallel jobs
        if self.task_count > 1:
            name, ext = os.path.splitext(blob_name)
            blob_name = f"{name}-{self.task_index:05d}{ext}"

        blob = bucket.blob(blob_name)

        # Write as a single string
        content = '\n'.join(output_lines)
        blob.upload_from_string(content, content_type=content_type)

        uri = f"gs://{bucket_name}/{blob_name}"
        logger.info(f"Wrote output to {uri}")
        return uri


def run_job(
    job_class: Type[Job],
    entity_kind: str,
    filters: Optional[List[tuple]] = None,
    **kwargs,
) -> None:
    """
    Convenience function to run a job.

    This is the main entry point for Cloud Run Job containers.

    Args:
        job_class: The Job class to instantiate and run
        entity_kind: Datastore entity kind to process
        filters: Optional query filters
        **kwargs: Additional arguments passed to run_from_datastore
    """
    job = job_class()
    runner = JobRunner(job)
    runner.run_from_datastore(entity_kind, filters=filters, **kwargs)

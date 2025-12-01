"""
Metrics tracking for Cloud Run Jobs.

Replaces MapReduce counters with in-memory tracking and optional
Cloud Monitoring integration.
"""

import logging
import os
from collections import defaultdict
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class JobMetrics:
    """
    In-memory counter implementation for job metrics.

    Replaces MapReduce op.counters.Increment with a simple dict-based
    counter that can optionally export to Cloud Monitoring.
    """

    def __init__(self, job_name: Optional[str] = None):
        self.job_name = job_name or os.environ.get('CLOUD_RUN_JOB', 'unknown')
        self._counters: Dict[str, int] = defaultdict(int)

    def increment(self, key: str, delta: int = 1) -> None:
        """
        Increment a counter.

        Args:
            key: Counter name
            delta: Amount to increment (default 1)
        """
        self._counters[key] += delta

    def get(self, key: str) -> int:
        """
        Get the current value of a counter.

        Args:
            key: Counter name

        Returns:
            Current counter value (0 if not set)
        """
        return self._counters.get(key, 0)

    def get_all(self) -> Dict[str, int]:
        """
        Get all counter values.

        Returns:
            Dict of counter names to values
        """
        return dict(self._counters)

    def log_summary(self) -> None:
        """Log a summary of all counters."""
        logger.info(f"Job metrics for {self.job_name}:")
        for key, value in sorted(self._counters.items()):
            logger.info(f"  {key}: {value}")

    def export_to_cloud_monitoring(self) -> None:
        """
        Export metrics to Cloud Monitoring.

        This is optional and requires the google-cloud-monitoring package.
        """
        try:
            from google.cloud import monitoring_v3

            client = monitoring_v3.MetricServiceClient()
            project_name = f"projects/{os.environ.get('GOOGLE_CLOUD_PROJECT', 'dancedeets-hrd')}"

            for key, value in self._counters.items():
                # Create a custom metric descriptor if needed
                # This is a simplified version - full implementation would
                # create proper metric descriptors
                logger.info(f"Would export to Cloud Monitoring: {key}={value}")

        except ImportError:
            logger.warning("google-cloud-monitoring not installed, skipping export")
        except Exception as e:
            logger.error(f"Error exporting to Cloud Monitoring: {e}")


class GroupedMetrics:
    """
    Metrics that can be grouped by a key (e.g., city, time_period).

    Useful for ranking-style aggregations.
    """

    def __init__(self):
        self._groups: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def increment(self, group_key: str, counter_key: str, delta: int = 1) -> None:
        """
        Increment a counter within a group.

        Args:
            group_key: The group identifier (e.g., city name)
            counter_key: The counter name within the group
            delta: Amount to increment
        """
        self._groups[group_key][counter_key] += delta

    def get_group(self, group_key: str) -> Dict[str, int]:
        """Get all counters for a group."""
        return dict(self._groups.get(group_key, {}))

    def get_all_groups(self) -> Dict[str, Dict[str, int]]:
        """Get all groups and their counters."""
        return {k: dict(v) for k, v in self._groups.items()}

    def get_totals(self, counter_key: str) -> Dict[str, int]:
        """Get totals for a specific counter across all groups."""
        return {
            group_key: counters.get(counter_key, 0)
            for group_key, counters in self._groups.items()
            if counters.get(counter_key, 0) > 0
        }


# Global metrics instance for compatibility with old mr.increment() pattern
_current_metrics: Optional[JobMetrics] = None


def set_current_metrics(metrics: JobMetrics) -> None:
    """Set the current job metrics instance (for compatibility)."""
    global _current_metrics
    _current_metrics = metrics


def get_current_metrics() -> Optional[JobMetrics]:
    """Get the current job metrics instance."""
    return _current_metrics


def increment(key: str, delta: int = 1) -> None:
    """
    Increment a counter (compatibility wrapper).

    This provides the same interface as the old mr.increment() function.
    """
    if _current_metrics:
        _current_metrics.increment(key, delta)
    else:
        logger.warning(f"No current metrics context, cannot increment {key}")

"""
Facebook API utilities for Cloud Run Jobs.

Ported from dancedeets.util.fb_mapreduce to work with the new
Cloud Run Jobs framework instead of MapReduce.
"""

import datetime
import logging
import random
from typing import Any, Dict, List, Optional

from dancedeets import fb_api
from dancedeets.users import access_tokens

logger = logging.getLogger(__name__)


class FBJobContext:
    """
    Context for Facebook API access within a job.

    Replaces the MapReduce context-based token storage with explicit
    parameter passing.
    """

    def __init__(
        self,
        fb_uid: str,
        access_token: Optional[str] = None,
        access_tokens: Optional[List[str]] = None,
        allow_cache: bool = True,
        oldest_allowed: Optional[datetime.datetime] = None,
    ):
        self.fb_uid = fb_uid
        self._access_token = access_token
        self._access_tokens = access_tokens or []
        self.allow_cache = allow_cache
        self.oldest_allowed = oldest_allowed

    @property
    def access_token(self) -> str:
        """Get an access token, randomly selecting from pool if available."""
        if self._access_tokens:
            return random.choice(self._access_tokens)
        return self._access_token or ''

    def get_fblookup(self, user: Optional[Any] = None) -> fb_api.FBLookup:
        """
        Create an FBLookup instance for API calls.

        Args:
            user: Optional user object with fb_uid and fb_access_token

        Returns:
            Configured FBLookup instance
        """
        if user:
            uid = user.fb_uid
            token = user.fb_access_token or self.access_token
        else:
            uid = self.fb_uid
            token = self.access_token

        fbl = fb_api.FBLookup(uid, token)
        fbl.allow_cache = self.allow_cache

        if self.oldest_allowed is not None:
            fbl.db.oldest_allowed = self.oldest_allowed

        return fbl


def get_fblookup_params(
    fbl: fb_api.FBLookup,
    randomize_tokens: bool = False,
    token_count: int = 50,
) -> Dict[str, Any]:
    """
    Extract parameters from an FBLookup for job configuration.

    This creates a serializable dict that can be passed to job constructors.

    Args:
        fbl: Source FBLookup instance
        randomize_tokens: If True, fetch multiple tokens for rotation
        token_count: Number of tokens to fetch when randomizing

    Returns:
        Dict of parameters for FBJobContext
    """
    params = {
        'fb_uid': fbl.fb_uid,
        'allow_cache': fbl.allow_cache,
    }

    if fbl.db.oldest_allowed != datetime.datetime.min:
        params['oldest_allowed'] = fbl.db.oldest_allowed

    if randomize_tokens:
        tokens = get_multiple_tokens(token_count=token_count)
        logger.info(f'Found {len(tokens)} valid tokens')
        if len(tokens) == 0:
            raise Exception('No Valid Tokens')
        params['access_tokens'] = tokens
    else:
        params['access_token'] = fbl.access_token

    return params


def get_multiple_tokens(token_count: int = 50) -> List[str]:
    """
    Get multiple valid access tokens for token rotation.

    For long-running jobs, using multiple tokens helps avoid rate limiting.

    Args:
        token_count: Maximum number of tokens to return

    Returns:
        List of valid access token strings
    """
    return access_tokens.get_multiple_tokens(token_count=token_count)


def get_fblookup(
    fb_uid: str,
    access_token: Optional[str] = None,
    access_tokens: Optional[List[str]] = None,
    allow_cache: bool = True,
    oldest_allowed: Optional[datetime.datetime] = None,
    user: Optional[Any] = None,
) -> fb_api.FBLookup:
    """
    Create an FBLookup instance for API calls.

    This is a convenience function that mirrors the old MapReduce pattern.

    Args:
        fb_uid: Facebook user ID
        access_token: Single access token
        access_tokens: List of tokens for rotation
        allow_cache: Whether to use caching
        oldest_allowed: Oldest cache entry to accept
        user: Optional user object to get token from

    Returns:
        Configured FBLookup instance
    """
    ctx = FBJobContext(
        fb_uid=fb_uid,
        access_token=access_token,
        access_tokens=access_tokens,
        allow_cache=allow_cache,
        oldest_allowed=oldest_allowed,
    )
    return ctx.get_fblookup(user=user)


def create_fb_context_from_fbl(
    fbl: fb_api.FBLookup,
    randomize_tokens: bool = False,
) -> FBJobContext:
    """
    Create an FBJobContext from an existing FBLookup.

    Useful when starting a job from a web request handler that already
    has an authenticated FBLookup.

    Args:
        fbl: Source FBLookup instance
        randomize_tokens: If True, fetch multiple tokens for rotation

    Returns:
        FBJobContext configured from the FBLookup
    """
    params = get_fblookup_params(fbl, randomize_tokens=randomize_tokens)
    return FBJobContext(
        fb_uid=params['fb_uid'],
        access_token=params.get('access_token'),
        access_tokens=params.get('access_tokens'),
        allow_cache=params['allow_cache'],
        oldest_allowed=params.get('oldest_allowed'),
    )

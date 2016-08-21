/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import fetch from 'node-fetch';

const YoutubeKey = 'AIzaSyCV8QCRxSwv1vVk017qI3EZ9zlC8TefUjY';

function getUrl(path: string, args: Object) {
  const querystring = require('querystring');
  const formattedArgs = querystring.stringify(args);
  var fullPath = path;
  if (formattedArgs) {
    fullPath += '?' + formattedArgs;
  }
  return fullPath;
}


async function getTimes(playlistItemsJson) {
  const videoIds = playlistItemsJson.items.map((x) => x.snippet.resourceId.videoId);
  const playlistItemsUrl = getUrl('https://www.googleapis.com/youtube/v3/videos',
  {
    id: videoIds.join(','),
    maxResults: 50,
    part: 'contentDetails',
    key: YoutubeKey,
  });
  const videosResult = await (await fetch(playlistItemsUrl)).json();
  return videosResult;
}

async function load(playlistId) {
  const playlistItemsUrl = getUrl('https://www.googleapis.com/youtube/v3/playlistItems',
  {
    playlistId: playlistId,
    maxResults: 50,
    part: 'snippet',
    key: YoutubeKey,
  });
  const playlistItemsJson = await (await fetch(playlistItemsUrl)).json();
  const videosJson = await getTimes(playlistItemsJson);

  const contentDetailsLookup = {};
  videosJson.items.forEach((x) => {
    contentDetailsLookup[x.id] = x.contentDetails;
  });
  // Filter out any private/deleted videos which we can't access contentDetails for
  const filteredPlaylistItems = playlistItemsJson.items
    .filter((x) => contentDetailsLookup[x.snippet.resourceId.videoId]);
  const annotatedPlaylist = filteredPlaylistItems.map((x) => {
    return {
      id: x.snippet.resourceId.videoId,
      duration: contentDetailsLookup[x.snippet.resourceId.videoId].duration,
      title: x.snippet.title,
    };
  });
  console.log(JSON.stringify(annotatedPlaylist, null, '  '));
}


load(process.argv.slice(2));

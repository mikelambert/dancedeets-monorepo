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
  const videoIds = playlistItemsJson.items.map((x) => x.id instanceof Object ? x.id.videoId : x.snippet.resourceId.videoId);
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

async function loadPlaylist(playlistId) {
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

async function loadChannel(channelName, searchQuery) {
  const channelUrl = getUrl('https://www.googleapis.com/youtube/v3/channels',
  {
    forUsername: channelName,
    part: 'snippet',
    key: YoutubeKey,
  });
  const channelJson = await (await fetch(channelUrl)).json();
  const channelId = channelJson.items[0].id;
  const channelSearchUrl = getUrl('https://www.googleapis.com/youtube/v3/search',
  {
    channelId,
    part: 'id,snippet',
    q: searchQuery,
    key: YoutubeKey,
    maxResults: 50,
    type: 'video',
  });
  const channelSearchJson = await (await fetch(channelSearchUrl)).json();
  const videosJson = await getTimes(channelSearchJson);
  const contentDetailsLookup = {};
  videosJson.items.forEach((x) => {
    contentDetailsLookup[x.id] = x.contentDetails;
  });
  const annotatedPlaylist = channelSearchJson.items.map((x) => {
    const id = x.id instanceof Object ? x.id.videoId : x.snippet.resourceId.videoId;
    return {
      id: id,
      duration: contentDetailsLookup[id].duration,
      title: x.snippet.title,
    };
  });
  console.log(JSON.stringify(annotatedPlaylist, null, '  '));
}

const args = process.argv.slice(2);
const type = args[0];
if (type == 'pl') {
  loadPlaylist(args[1]);
} else if (type == 'ch') {
  loadChannel(args[1], args[2]);
}

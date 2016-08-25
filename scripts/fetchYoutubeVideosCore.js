/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';
import _ from 'underscore';
import fetch from 'node-fetch';

export const YoutubeKey = 'AIzaSyCV8QCRxSwv1vVk017qI3EZ9zlC8TefUjY';

export function getUrl(path: string, args: Object) {
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
  const returnResult = {
    items: [],
  };
  while (videoIds.length) {
    const splicedVideoIds = videoIds.splice(0, 50);
    const playlistItemsUrl = getUrl('https://www.googleapis.com/youtube/v3/videos',
    {
      id: splicedVideoIds.join(','),
      maxResults: 50,
      part: 'contentDetails',
      key: YoutubeKey,
    });
    const videosResult = await (await fetch(playlistItemsUrl)).json();
    Array.prototype.push.apply(returnResult.items, videosResult.items);
  }
  return returnResult;
}

export async function loadPlaylist(playlistId) {
  const playlistItemsUrl = getUrl('https://www.googleapis.com/youtube/v3/playlistItems',
  {
    playlistId: playlistId,
    maxResults: 50,
    part: 'snippet',
    key: YoutubeKey,
  });
  const playlistItemsJson = await fetchAll(playlistItemsUrl);
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
      youtubeId: x.snippet.resourceId.videoId,
      duration: contentDetailsLookup[x.snippet.resourceId.videoId].duration,
      title: x.snippet.title,
    };
  });
  return annotatedPlaylist;
}

async function printPlaylist(playlistId) {
  printResult(await loadPlaylist(playlistId));
}

async function fetchAll(pageUrl, pageToken) {
  const newUrl = pageUrl + (pageToken ? '&pageToken=' + pageToken : '');
  const pageJson = await (await fetch(newUrl)).json();
  if (pageJson.nextPageToken) {
    const pageJson2 = await fetchAll(pageUrl, pageJson.nextPageToken);
    Array.prototype.push.apply(pageJson.items, pageJson2.items);
  }
  return pageJson;
}

async function loadChannel(channelName, searchQuery) {
  const channelUrl = getUrl('https://www.googleapis.com/youtube/v3/channels',
  {
    forUsername: channelName,
    part: 'snippet',
    key: YoutubeKey,
  });
  const channelJson = await (await fetch(channelUrl)).json();
  const channelId = channelJson.items.length ? channelJson.items[0].id : channelName;
  const channelSearchUrl = getUrl('https://www.googleapis.com/youtube/v3/search',
  {
    channelId,
    part: 'id,snippet',
    q: searchQuery,
    key: YoutubeKey,
    maxResults: 50,
    type: 'video',
  });
  const channelSearchJson = await fetchAll(channelSearchUrl);
  const videosJson = await getTimes(channelSearchJson);
  const contentDetailsLookup = {};
  videosJson.items.forEach((x) => {
    contentDetailsLookup[x.id] = x.contentDetails;
  });
  const annotatedPlaylist = channelSearchJson.items.map((x) => {
    const id = x.id instanceof Object ? x.id.videoId : x.snippet.resourceId.videoId;
    return {
      youtubeId: id,
      duration: contentDetailsLookup[id] ? contentDetailsLookup[id].duration : null,
      title: x.snippet.title,
      publishedAt: x.snippet.publishedAt,
    };
  });
  const searchKeywords = searchQuery.split(' ');
  const filteredPlaylist = annotatedPlaylist.filter((x) => {
    for (var i = 0; i < searchKeywords.length; i++) {

      if (x.title.toLowerCase().indexOf(searchKeywords[i]) == -1) {
        return false;
      }
    }
    return true;
  });
  const sortedPlaylist = _.sortBy(filteredPlaylist, 'publishedAt').map((x) => _.omit(x, 'publishedAt'));
  return sortedPlaylist;
}

async function printChannel(channelName, searchQuery) {
  printResult(await loadChannel(channelName, searchQuery));
}

function printResult(videos) {
  const result = {
    title: '',
    videos: videos,
  };
  console.log(JSON.stringify(result, null, '  '));
}

const args = process.argv.slice(2);
const type = args[0];
if (type == 'pl') {
  printPlaylist(args[1]);
} else if (type == 'ch') {
  printChannel(args[1], args[2]);
}

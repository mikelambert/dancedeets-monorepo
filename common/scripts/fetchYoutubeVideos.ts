#!/usr/bin/awk BEGIN{a=b=ARGV[1];sub(/[A-Za-z_.]+$/,"../../runNode.js",a);sub(/^.*\//,"./",b);system(a"\t"b)}

/**
 * Copyright 2016 DanceDeets.
 */
import _ from 'underscore';
import fetch from 'node-fetch';
import querystring from 'querystring';
import { fetchAll, getUrl, YoutubeKey } from './_youtube';

interface PlaylistItem {
  id: string | { videoId: string };
  snippet: {
    resourceId: { videoId: string };
    title: string;
    publishedAt?: string;
  };
}

interface PlaylistItemsJson {
  items: PlaylistItem[];
}

interface VideoItem {
  id: string;
  contentDetails: {
    duration: string;
  };
}

interface VideosResult {
  items: VideoItem[];
}

interface AnnotatedVideo {
  youtubeId: string;
  duration: string;
  title: string;
  publishedAt?: string;
}

async function getTimes(playlistItemsJson: PlaylistItemsJson): Promise<VideosResult> {
  const videoIds = playlistItemsJson.items.map(
    x => (x.id instanceof Object ? x.id.videoId : x.snippet.resourceId.videoId)
  );
  const returnResult: VideosResult = {
    items: [],
  };
  while (videoIds.length) {
    // modifies videoIds
    const splicedVideoIds = videoIds.splice(0, 50);
    const playlistItemsUrl = getUrl(
      'https://www.googleapis.com/youtube/v3/videos',
      {
        id: splicedVideoIds.join(','),
        maxResults: 50,
        part: 'contentDetails',
        key: YoutubeKey,
      }
    );
    const videosResult: VideosResult = await (await fetch(playlistItemsUrl)).json();
    Array.prototype.push.apply(returnResult.items, videosResult.items);
  }
  return returnResult;
}

export async function loadPlaylist(playlistId: string): Promise<AnnotatedVideo[]> {
  const playlistItemsUrl = getUrl(
    'https://www.googleapis.com/youtube/v3/playlistItems',
    {
      playlistId,
      maxResults: 50,
      part: 'snippet',
      key: YoutubeKey,
    }
  );
  const playlistItemsJson = await fetchAll(playlistItemsUrl) as PlaylistItemsJson;
  const videosJson = await getTimes(playlistItemsJson);
  const contentDetailsLookup: Record<string, { duration: string }> = {};
  videosJson.items.forEach(x => {
    contentDetailsLookup[x.id] = x.contentDetails;
  });
  // Filter out any private/deleted videos which we can't access contentDetails for
  const filteredPlaylistItems = playlistItemsJson.items.filter(
    x => contentDetailsLookup[x.snippet.resourceId.videoId]
  );
  const annotatedPlaylist: AnnotatedVideo[] = filteredPlaylistItems.map(x => ({
    youtubeId: x.snippet.resourceId.videoId,
    duration: contentDetailsLookup[x.snippet.resourceId.videoId].duration,
    title: x.snippet.title,
  }));
  return annotatedPlaylist;
}

async function printPlaylist(playlistId: string): Promise<void> {
  printResult(await loadPlaylist(playlistId));
}

interface ChannelJson {
  items: Array<{ id: string }>;
}

interface SearchItem {
  id: string | { videoId: string };
  snippet: {
    resourceId?: { videoId: string };
    title: string;
    publishedAt: string;
  };
}

interface ChannelSearchJson {
  items: SearchItem[];
}

async function loadChannel(channelName: string, searchQuery: string): Promise<Omit<AnnotatedVideo, 'publishedAt'>[]> {
  const channelUrl = getUrl('https://www.googleapis.com/youtube/v3/channels', {
    forUsername: channelName,
    part: 'snippet',
    key: YoutubeKey,
  });
  const channelJson: ChannelJson = await (await fetch(channelUrl)).json();
  const channelId = channelJson.items.length
    ? channelJson.items[0].id
    : channelName;
  const channelSearchUrl = getUrl(
    'https://www.googleapis.com/youtube/v3/search',
    {
      channelId,
      part: 'id,snippet',
      q: searchQuery,
      key: YoutubeKey,
      maxResults: 50,
      type: 'video',
    }
  );
  const channelSearchJson = await fetchAll(channelSearchUrl) as ChannelSearchJson;
  const videosJson = await getTimes(channelSearchJson as unknown as PlaylistItemsJson);
  const contentDetailsLookup: Record<string, { duration: string }> = {};
  videosJson.items.forEach(x => {
    contentDetailsLookup[x.id] = x.contentDetails;
  });
  const annotatedPlaylist: AnnotatedVideo[] = channelSearchJson.items.map(x => {
    const id =
      x.id instanceof Object ? x.id.videoId : (x.snippet.resourceId?.videoId || '');
    return {
      youtubeId: id,
      duration: contentDetailsLookup[id]
        ? contentDetailsLookup[id].duration
        : '',
      title: x.snippet.title,
      publishedAt: x.snippet.publishedAt,
    };
  });
  const searchKeywords = searchQuery.split(' ');
  const filteredPlaylist = annotatedPlaylist.filter(x => {
    for (const keyword of searchKeywords) {
      if (x.title.indexOf(keyword) === -1) {
        return false;
      }
    }
    return true;
  });
  const sortedPlaylist = _.sortBy(filteredPlaylist, 'publishedAt').map(x =>
    _.omit(x, 'publishedAt')
  );
  return sortedPlaylist;
}

async function printChannel(channelName: string, searchQuery: string): Promise<void> {
  printResult(await loadChannel(channelName, searchQuery));
}

function printResult(videos: Array<Omit<AnnotatedVideo, 'publishedAt'>>): void {
  const result = {
    title: '',
    videos,
  };
  console.log(JSON.stringify(result, null, '  '));
}

const args = process.argv.slice(2);
const type = args[1];
if (type === 'pl') {
  printPlaylist(args[2]);
} else if (type === 'ch') {
  printChannel(args[2], args[3] || '');
}

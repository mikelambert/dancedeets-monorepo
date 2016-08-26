/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';
import _ from 'underscore';
import fetch from 'node-fetch';
import querystring from 'querystring';

export const YoutubeKey = 'AIzaSyCV8QCRxSwv1vVk017qI3EZ9zlC8TefUjY';

export function getUrl(path: string, args: Object) {
  const formattedArgs = querystring.stringify(args);
  var fullPath = path;
  if (formattedArgs) {
    fullPath += '?' + formattedArgs;
  }
  return fullPath;
}

async function findVideoIds(videoIds): Promise<[string]> {
  const items = [];
  while (videoIds.length) {
    const splicedVideoIds = videoIds.splice(0, 50);
    const playlistItemsUrl = getUrl('https://www.googleapis.com/youtube/v3/videos',
    {
      id: splicedVideoIds.join(','),
      maxResults: 50,
      part: 'id',
      key: YoutubeKey,
    });
    const videosResult = await (await fetch(playlistItemsUrl)).json();
    Array.prototype.push.apply(items, videosResult.items);
  }
  return items.map((x) => x.id);
}

async function checkTutorial(tutorialJson) {
  const videoIds = [];
  for (let section of tutorialJson.sections) {
    for (let video of section.videos) {
      videoIds.push(video.youtubeId);
    }
  }
  const thumbnailVideoId = videoIds.find((videoId) => tutorialJson.thumbnail == `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`);
  if (!thumbnailVideoId) {
    console.error('Thumbnail for tutorial set incorrectly:', tutorialJson.style, tutorialJson.title);
  }
  const foundVideoIds = new Set(await findVideoIds(videoIds));
  const missingVideoIds = videoIds.filter(x => !foundVideoIds.has(x));
  if (missingVideoIds.length) {
    console.error('Tutorial has broken video references: ', missingVideoIds);
  }
}

//    const filename = `./js/learn/break/vincanitv_${playlistTitle.replace(' ', '').toLowerCase()}.json`;
//    fs.writeFile(filename, JSON.stringify(tutorial, null, '  '));

const a = require('../js/learn/break/footworkfundamentals.json');
console.log(a);
checkTutorial(a);

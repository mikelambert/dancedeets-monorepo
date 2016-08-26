/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';
import fetch from 'node-fetch';
import querystring from 'querystring';
import { walk, readFile } from './_fsPromises';
import parseJson from 'parse-json';
import areEqual from 'fbjs/lib/areEqual';

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


async function checkAllTutorials() {
  const files = await walk('js/learn/tutorials');
  const jsonFiles = files.filter((x) => x.endsWith('.json'));
  const promises = [];
  const tutorials = [];
  for (let jsonFilename of jsonFiles) {
    let jsonData = null;
    try {
      jsonData = parseJson(await readFile(jsonFilename));
      tutorials.push(jsonData);
    } catch (e) {
      console.error('Error loading ', jsonFilename, '\n', e);
      continue;
    }
    promises.push(checkTutorial(jsonData));
  }
  await Promise.all(promises);

  // Used for testing down below
  let defaultTutorials = null;
  try {
    defaultTutorials = require('../js/learn/learnConfig.js').defaultTutorials;
  } catch (e) {
    console.error('Error importing learnConfig.js\n', e);
  }
  const configuredTutorials = [].concat.apply([], Object.values(defaultTutorials));
  const missingTutorials = tutorials.filter((fileTut) => !configuredTutorials.find((configTut) => areEqual(configTut, fileTut)));
  for (let tutorial of missingTutorials) {
    console.error('Tutorial not included: ', tutorial.style, tutorial.title);
  }
}

checkAllTutorials();

/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';
import fetch from 'node-fetch';
import querystring from 'querystring';
import {
  readFile,
  walk,
  writeFile,
} from './_fsPromises';
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

async function findVideoItems(inVideoIds): Promise<[Object]> {
  const items = [];
  const videoIds = inVideoIds.slice();
  while (videoIds.length) {
    // modifies videoIds
    const splicedVideoIds = videoIds.splice(0, 50);
    const playlistItemsUrl = getUrl('https://www.googleapis.com/youtube/v3/videos',
    {
      id: splicedVideoIds.join(','),
      maxResults: 50,
      part: 'id,contentDetails',
      key: YoutubeKey,
    });
    const videosResult = await (await fetch(playlistItemsUrl)).json();
    Array.prototype.push.apply(items, videosResult.items);
  }
  return items;
}

async function findVideoDimensions(videoIds) {
  const dimensions = {};
  for (let videoId of videoIds) {
    const oEmbedUrl = `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`;
    const results = await (await fetch(oEmbedUrl)).json();
    dimensions[videoId] = {width: results.width, height: results.height};
  }
  return dimensions;
}

async function checkTutorial(tutorialJson) {
  const videoIds = [];
  for (let section of tutorialJson.sections) {
    for (let video of section.videos) {
      videoIds.push(video.youtubeId);
    }
  }
  const thumbnailVideoId = videoIds.find((videoId) => tutorialJson.thumbnail == `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`);
  if (!thumbnailVideoId) {
    console.error('Thumbnail for tutorial set incorrectly:', tutorialJson.style, tutorialJson.title);
  }
  const videoItems = await findVideoItems(videoIds);
  const videoItemsMap = {};
  for (let video of videoItems) {
    videoItemsMap[video.id] = video;
  }

  const videoDimensionsMap = await findVideoDimensions(videoIds);

  for (let section of tutorialJson.sections) {
    for (let video of section.videos) {
      const foundVideo = videoItemsMap[video.youtubeId];
      // Check that each video id exists
      if (!foundVideo) {
        console.error(`Tutorial ${video.youtubeId} has broken video reference.`);
      // Check that video durations are correct
      } else if (video.duration != foundVideo.contentDetails.duration) {
        console.error(`Tutorial ${video.youtubeId} has incorrect duration: ${video.duration}, expected: ${foundVideo.contentDetails.duration}`);
        video.duration = foundVideo.contentDetails.duration;
      }

      const foundOEmbed = videoDimensionsMap[video.youtubeId];
      // Check that each video id exists
      if (!foundOEmbed) {
        console.error(`Tutorial ${video.youtubeId} has broken oembed video reference.`);
        continue;
      // Check that video dimensions are correct
      } else if (video.width !== foundOEmbed.width || video.height !== foundOEmbed.height) {
        console.error(`Tutorial ${video.youtubeId} has incorrect dimensions: ${video.width}x${video.height}, expected: ${foundOEmbed.width}x${foundOEmbed.height}`);
        video.height = foundOEmbed.height;
        video.width = foundOEmbed.width;
      }
    }
  }
  return tutorialJson;
}

async function reportAndFix(jsonFilename, jsonData) {
  const fixedJson = await checkTutorial(jsonData);
  await writeFile(jsonFilename, JSON.stringify(fixedJson, null, '  '));
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
    promises.push(reportAndFix(jsonFilename, jsonData));
  }
  await Promise.all(promises);

  // Used for testing down below
  let defaultTutorials = null;
  try {
    defaultTutorials = require('../js/learn/learnConfig.js').defaultTutorials;
  } catch (e) {
    console.error('Error importing learnConfig.js\n', e);
    return;
  }
  const configuredTutorials = [].concat.apply([], Object.values(defaultTutorials.map((style) => style.tutorials)));
  const missingTutorials = tutorials.filter((fileTut) => !configuredTutorials.find((configTut) => areEqual(configTut, fileTut)));
  for (let tutorial of missingTutorials) {
    console.error('Tutorial not included: ', tutorial.style, tutorial.title);
  }
  console.log('Finished!');
}

checkAllTutorials();

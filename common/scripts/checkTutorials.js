#!/usr/bin/awk BEGIN{a=b=ARGV[1];sub(/[A-Za-z_.]+$/,"../../runNode.js",a);sub(/^.*\//,"./",b);system(a"\t"b)}

/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
import fetch from 'node-fetch';
import querystring from 'querystring';
import parseJson from 'parse-json';
import areEqual from 'fbjs/lib/areEqual';
import fs from 'fs-promise';
import {
  findVideoDimensions,
  getUrl,
  YoutubeKey,
} from './_youtube';

async function findVideoItems(inVideoIds): Promise<Object[]> {
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
    try {
      const videosResult = await (await fetch(playlistItemsUrl)).json();
      Array.prototype.push.apply(items, videosResult.items);
    } catch (err) {
      console.error(playlistItemsUrl, err);
    }
  }
  return items;
}

async function checkTutorial(tutorialJson) {
  const videoIds = [];
  for (const section of tutorialJson.sections) {
    for (const video of section.videos) {
      videoIds.push(video.youtubeId);
    }
  }
  const thumbnailVideoId = videoIds.find(videoId => tutorialJson.thumbnail === `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`);
  if (!thumbnailVideoId) {
    console.error('Thumbnail for tutorial set incorrectly:', tutorialJson.style, tutorialJson.title);
  }
  const videoItems = await findVideoItems(videoIds);
  const videoItemsMap = {};
  for (const video of videoItems) {
    videoItemsMap[video.id] = video;
  }

  const videoDimensionsMap = await findVideoDimensions(videoIds);

  for (const section of tutorialJson.sections) {
    for (const video of section.videos) {
      const foundVideo = videoItemsMap[video.youtubeId];
      // Check that each video id exists
      if (!foundVideo) {
        console.error(`Tutorial ${video.youtubeId} has broken video reference.`);
      // Check that video durations are correct
      } else if (video.duration !== foundVideo.contentDetails.duration) {
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
  try {
    const fixedJson = await checkTutorial(jsonData);
    await fs.writeFile(jsonFilename, JSON.stringify(fixedJson, null, '  '));
  } catch (err) {
    console.error('Error checking tutorial:', jsonFilename, ': ', err.stack);
    throw err;
  }
}

async function checkAllTutorials() {
  const files = (await fs.walk('../js/tutorials/playlists')).map(x => x.path);
  const jsonFiles = files.filter(x => x.endsWith('.json'));
  const promises = [];
  const tutorials = [];
  for (const jsonFilename of jsonFiles) {
    let jsonData = null;
    try {
      jsonData = parseJson(await fs.readFile(jsonFilename));
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
    defaultTutorials = require('../js/tutorials/playlistConfig.js').getTutorials('');
  } catch (e) {
    console.error('Error importing learnConfig.js\n', e);
    return;
  }
  const configuredTutorials = [].concat(...Object.values(defaultTutorials.map(style => style.tutorials)));
  const missingTutorials = tutorials.filter(fileTut => !configuredTutorials.find(configTut => configTut.id === fileTut.id));
  for (const tutorial of missingTutorials) {
    console.error('Tutorial not included: ', tutorial.style, tutorial.title);
  }
  console.log('Finished!');
}

checkAllTutorials();

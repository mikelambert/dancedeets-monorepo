#!/usr/bin/awk BEGIN{a=b=ARGV[1];sub(/[A-Za-z_.]+$/,"../../runNode.js",a);sub(/^.*\//,"./",b);system(a"\t"b)}

/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import {
  fetchAll,
  getUrl,
  YoutubeKey,
} from './_youtube';
import {
  Bracket
} from '../../server/assets/js/bracketModels';

const regexes = {
  final: /\bfinal\b/i,
  top4: /\b(?:(?:semi|1\s*\/\s*2)\W?final|(?:best|top)\W?4)\b/i,
  top8: /\b(?:(?:quarter|qtr|1\s*\/\s*4)\W?final|(?:best|top)\W?8)\b/i,
  top16: /\b(?:(?:quarter|qtr|1\s*\/\s*4)\W?final|(?:best|top)\W?16)\b/i,
};

const vsRegex = /\bv\W?[zs]\b|versus|\bx\b|\b×\b/i;

async function getPlaylistVideos(playlistId) {
  const playlistItemsUrl = getUrl('https://www.googleapis.com/youtube/v3/playlistItems',
    {
      playlistId,
      maxResults: 50,
      part: 'snippet',
      key: YoutubeKey,
    });
  const playlistItemsJson = await fetchAll(playlistItemsUrl);
  return playlistItemsJson;
}

async function run() {
  const result = await getPlaylistVideos('PL02EtzYP5EDOsZyptcmO8G-aPwsOAu9pO');
  const battleVideos = result.items.map(x => ({
    title: x.snippet.title,
    videoId: x.id,
  }));

  const bracket = new Bracket();
  const order = [regexes.final, regexes.top4, regexes.top8, regexes.top16];
  order.forEach((roundRegex, index) => {
    const expectedCount = 2 ** index;
    const matchedVideos = battleVideos.filter(x => roundRegex.test(x.title));
    if (matchedVideos.length != expectedCount) {
      console.log(matchedVideos)
    }
    matchedVideos.forEach(video => {
      const components = video.title.split(roundRegex);
      const contestantString = components.filter(x => vsRegex.test(x))[0];
      const contestants = contestantString.split(vsRegex).map(x => x.trim());
      console.log(contestants);

      bracket.matches.push({
        youtubeId: video.videoId,
        first: contestants[0],
        second: contestants[1],
      });
    })
  });
  console.log(JSON.stringify(bracket.matches));
}

run();
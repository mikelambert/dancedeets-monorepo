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
import type {
  Bracket,
  Match,
} from '../../server/assets/js/bracketModels';

const roundRegexes = {
  final: /\bfinal\b/i,
  top4: /\b(?:(?:semi|1\s*\/\s*2)\W?final|(?:best|top)\W?4)\b/i,
  top8: /\b(?:(?:quarter|qtr|1\s*\/\s*4)\W?final|(?:best|top)\W?8)\b/i,
  top16: /\b(?:(?:quarter|qtr|1\s*\/\s*4)\W?final|(?:best|top)\W?16)\b/i,
};

const anyRoundRegex = new RegExp(Object.values(roundRegexes).map(x => x.source).join('|'), 'i');

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

function getContestants(video) {
  const components = video.title.split(anyRoundRegex);
  const contestantString = components.filter(x => vsRegex.test(x))[0];
  const contestants = contestantString.split(vsRegex).map(x => x.trim());
  if (contestants.length !== 2) {
    console.error('Video:', video, 'found too many contestants:', contestants);
  }
  //TODO: HACK:
  const finalContestants = contestants.map(x => x.replace(' EX', '').replace(/\(.*\)/, ''));
  return finalContestants;
}

function getUniqueMatchesForRound(battleVideos, roundRegex, index): Array<Match> {
  const roundMatchCount = 2 ** index;
  const roundVideos = battleVideos.filter(x => roundRegex.test(x.title));
  if (roundVideos.length != roundMatchCount) {
    console.error('Found too many videos for round!', roundVideos);
  }
  const seenContestants = [];
  const roundMatches = [];
  roundVideos.forEach(video => {
    const contestants = getContestants(video);
    if (seenContestants.includes(contestants[0]) || seenContestants.includes(contestants[1])) {
      return;
    }
    seenContestants.push(contestants[0]);
    seenContestants.push(contestants[1]);
    roundMatches.push({
      youtubeId: video.videoId,
      first: contestants[0],
      second: contestants[1],
    });
  });
  return roundMatches;
}

async function run() {
  const result = await getPlaylistVideos('PL02EtzYP5EDOsZyptcmO8G-aPwsOAu9pO');
  const battleVideos = result.items.map(x => ({
    title: x.snippet.title,
    videoId: x.snippet.resourceId.videoId,
  }));

  const bracket: Bracket = {};
  const order = [roundRegexes.final, roundRegexes.top4, roundRegexes.top8, roundRegexes.top16];

  let parentRoundContestantOrder = [];
  order.forEach((roundRegex, index) => {
    const foundMatches = getUniqueMatchesForRound(battleVideos, roundRegex, index);
    let sortedMatches = null;
    if (parentRoundContestantOrder.length) {
      sortedMatches = parentRoundContestantOrder.map(contestant => {
        const result = foundMatches.find(match => (
          match.first === contestant || match.second === contestant
        ));
        return result;
      });
    } else {
      sortedMatches = foundMatches;
    }
    console.log('round ', index);
    console.log(sortedMatches);
    parentRoundContestantOrder = [].concat(...sortedMatches.map(x => [x.first, x.second]));
  });
}

run();
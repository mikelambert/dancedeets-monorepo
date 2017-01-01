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
  if (!vsRegex.test(contestantString)) {
    console.error('Video:', video, 'does not contain a "vs"');
  }
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
  if (!roundVideos.length) {
    return [];
  }
  if (roundVideos.length > roundMatchCount) {
    console.error('Found too many videos for round!', roundVideos);
  }
  const seenContestants = [];
  const roundMatches: Array<Match> = [];
  roundVideos.forEach(video => {
    const contestants = getContestants(video);
    if (seenContestants.includes(contestants[0]) || seenContestants.includes(contestants[1])) {
      return;
    }
    seenContestants.push(contestants[0]);
    seenContestants.push(contestants[1]);
    roundMatches.push({
      videoId: video.videoId,
      first: contestants[0],
      second: contestants[1],
    });
  });
  return roundMatches;
}

async function buildBracketFromPlaylist(playlistId) {
  const result = await getPlaylistVideos(playlistId);
  const battleVideos = result.items.map(x => ({
    title: x.snippet.title,
    videoId: x.snippet.resourceId.videoId,
  }));

  const bracket: Bracket = {
    matches: []
  };
  const order = [roundRegexes.final, roundRegexes.top4, roundRegexes.top8, roundRegexes.top16];

  let parentRoundContestantOrder = [];
  order.forEach((roundRegex, index) => {
    const foundMatches = getUniqueMatchesForRound(battleVideos, roundRegex, index);
    if (!foundMatches.length) {
      return;
    }
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
    bracket.matches.push(...sortedMatches);
    parentRoundContestantOrder = [].concat(...sortedMatches.map(x => x ? [x.first, x.second] : [null, null]));
  });
  return bracket;
}

// Should we handle prelims/preliminaries/circle A/B/C/D/etc videos?
// Should we handle judge demos too?
// We should do a better job of handling EX extra rounds

// PL02EtzYP5EDOsZyptcmO8G-aPwsOAu9pO works
// PL02EtzYP5EDOznUxhAPUi7agKWhHeUlsV works
// PL02EtzYP5EDP8ibrNzJqDhnh0x-R8l8Pi works
// PL02EtzYP5EDNxn_TWy_QPg4CTOwyd_mVh works
// PL02EtzYP5EDNXRVIYOmn9JE00s-MtFVy9 works
// PL02EtzYP5EDNC-tR53BwZO-nbacCft-Rt works
// PL02EtzYP5EDO1IHqw_ugVZywWYMIUufZi works
// PL02EtzYP5EDNvxRLDTrv1gGq0VuCVetiH works
// PL02EtzYP5EDPo8t0XnbIjKJsc-xajp9p_ works
// PL02EtzYP5EDMXAyDtNBh-waUjty8Kc4jX works
// PL02EtzYP5EDPTN3fd1fclx6S23TizWiKT works
// PL02EtzYP5EDMe6_JOcNn-h8wED4AI8kP7 works

// PL02EtzYP5EDPmjF2qXLnvxNdgDGMDZmUW unfortunately contains the a 1v1 and 2v2 on the same playlist with no differentiation besides contestant names
// PL02EtzYP5EDO-McJJ-3zywQpKQUkbGlOH also seems to contain two parallel battles?

// PL02EtzYP5EDMsNcj1ayyIvhaf17D3CeT0 capitalization differences for contestant's name between rounds
// PL02EtzYP5EDNKWJfaSGyXqygewSynUl83 contestant name slightly different between rounds

// PL02EtzYP5EDPVY9y_Fl4RyF8xpaIFWBib (we should strip out common dance event title...as it may contain 'FINAL')
// PL02EtzYP5EDNdSMYOktajlXLemXd6TVHI
// PL02EtzYP5EDNGw4TDNwyPnJ2lX0Ea3r9R
// PL02EtzYP5EDPdK7fLFyyyzKlLqQ8iysus
// PL02EtzYP5EDMa06kzeJnCvh5uQZ_znsuL has FINALS. also has capitalization difference on DANIEL daniel. and has confusing finals 1-5

// PL02EtzYP5EDMjpUNvFH3ARZdO6hfdfNM0 some battles got taken-down (or not posted). can we deal with gaps?
// PL02EtzYP5EDPkZQ3pItIt6u5NxsMQ2Ib0 'best16 circle' screws up the matching
// PL02EtzYP5EDMq7lgawjIVDmXkYPYa0GTQ looks like a hot mess
// PL02EtzYP5EDNijB1DqdOxmRli8uDmg0jk best16 is actually a five-way?
// PL02EtzYP5EDN9B55sxhyGEg8z8MbJQeZa best16 is a four-way
// PL02EtzYP5EDONwwNOaDzh7zpCEgsKK8Pn best16 is sometimes multi-way, sometimes 1v1

async function run() {
  const bracket = await buildBracketFromPlaylist('PL02EtzYP5EDMe6_JOcNn-h8wED4AI8kP7');
  console.log(bracket);
}

run();
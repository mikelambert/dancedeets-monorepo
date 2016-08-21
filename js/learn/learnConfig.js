/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { RemoteConfig } from 'react-native-firebase3';

const defaultTutorials = [
  require('./house/jardy.json'),
  require('./house/rich.json'),
  require('./house/malcolm.json'),
  require('./house/alvaro.json'),
  require('./house/hiro.json'),
  require('./house/koji.json'),
  require('./house/yeomin.json'),
  require('./house/yusuke.json'),
  require('./house/vincanitv.json'),
  require('./house/japanese.json'),
  require('./house/miscellaneous.json'),
  require('./hiphop/alvaro.json'),
];

const defaultBlogs = [
  'y:PLZelnKT8VJwytJrZY9nmZtslGRdhFaYso', // Jardy in spanish (needs subtitles!)
  'y:PLF5290D54A54C4EDA', // Jardy in Korean (needs subtitles!)
  // Somehow some of these aren't in a playlist? https://www.youtube.com/user/DANCEcoaching/search?query=%E3%83%8F%E3%82%A6%E3%82%B9
  // In particular: https://www.youtube.com/watch?v=EEluQ_4eBrs

  'y:PL_eG_ziq86f_JuH3AvfAGi8qv9zn7T_nS', // japanese locking
  'y:PL2LmIWNts41gY1yYQDqh1e4LM4-GbiI-r', // a bunch of individual tutorials, should be split up!
  'y:PLNu-Tjbz985ZgTVzPpMFGpopYbxeLNNWn', // more OGs in here, no real 1/2/3/4/5 though
  'y:PL60B63DCF4C745EF4', // Originality Khan
  'y:PLD3786D9190A031C9', // Includes crap expertvillage as well as japanese ones
];

// Find many here:
// https://www.youtube.com/user/RISINGDanceSchoolCh/playlists
// https://www.youtube.com/playlist?list=PLGOtBlWsXfr1eGS2Z2_efsYG3mwpz0WPa
// https://www.youtube.com/user/DANCEdiet/playlists
// https://www.youtube.com/user/WEBDancelesson/playlists
// https://www.youtube.com/user/DANCEcoaching/playlists
// https://www.youtube.com/user/acrobatDANCE/playlists
// https://www.youtube.com/channel/UCAcWPeaHGnvFQvkCmlFK40A/playlists

// Also possibly this one
// https://www.youtube.com/user/ichidancerdesu2/videos

const extraBlogs = [
  'http://www.thebboyspot.com/feed/',
  'http://loftpractice.com/?format=feed&type=atom',
  'http://blog.steezy.co/feed/',
  'http://www.ilovethisdance.com/feed/',
  'http://www.stepxstepdance.com/feed/',
  'http://www.hiphopinternational.com/feed/',
  'http://www.udeftour.org/feed/',
  'https://studiogdmv.wordpress.com/feed/',
  //'http://www.dancedelight.net/wordpress/?feed=atom',
  'http://houseofmovementny.com/blog?format=RSS',
  'http://www.onecypher.com/feed/',
  'http://www.funkstylers.tv/feed/',
  'http://urbanartistrydc.blogspot.com/feeds/posts/default',
  'https://thespreadlovedanceproject.wordpress.com/feed/',
  'http://event.juste-debout.com/feed/',
  'http://www.juste-debout-tv.com/feed/',
  'https://wzhotdog.wordpress.com/feed/',
  'http://populathoughts.blogspot.com/feeds/posts/default',
  'http://fuckyeadance.tumblr.com/rss',
  'http://www.scramblelock.com/feed/',
  'http://dews365.com/feed',
  'http://www.dancemeets.com/feed/',
  // This is a Medium magazine
  'rue-magazine',
];

async function loadConfig() {
  RemoteConfig.setNamespacedDefaults({
    tutorials: JSON.stringify(defaultTutorials),
    blogs: JSON.stringify(defaultBlogs),
  }, 'Learn');
  await RemoteConfig.fetchWithExpirationDuration(30 * 15);
  await RemoteConfig.activateFetched();
}

loadConfig();

export async function getRemoteBlogs() {
  return JSON.parse(await RemoteConfig.getNamedspacedString('blogs', 'Learn'));
}
export async function getRemoteTutorials() {
  return JSON.parse(await RemoteConfig.getNamedspacedString('tutorials', 'Learn'));
}

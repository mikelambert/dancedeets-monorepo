/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { RemoteConfig } from 'react-native-firebase3';

const defaultBlogs = [
  'y:PLB9CAA2877007AC02', // House Jardy: basic
  'y:PLE839D54D07A8ABC2', // House Jardy: advanced
  'y:PLdu69DsTPMPSw7OWmDuKxuoYJeFl6HsmR', // House with Rich Stylez
  'y:PLwTkRR4yEsPL6g_GorhXIhM-uaL77sGjo', // House with Super Malcolm
  'y:PLZelnKT8VJwytJrZY9nmZtslGRdhFaYso', // Jardy in spanish (needs subtitles!)
  'y:PLF5290D54A54C4EDA', // Jardy in Korean (needs subtitles!)
  'y:PLVY6uOsv4D9aV0_xhKlb1HhmviRBaB4Uh', // Koji in Japanese
  'y:PLVY6uOsv4D9YVHGU8AAv4wlORDtNkAjIp', // Hiro in Japanese
  'y:PLomQfPiZA65Rh0hgchIytdZYlhxOaXfDm', // Yu-suke in Japanese
  'y:PLwQFrP9G-gpB-CO355_sKMF5EsKSWHwRc', // Yu-suke in Japanese
  // Somehow some of these aren't in a playlist? https://www.youtube.com/user/DANCEcoaching/search?query=%E3%83%8F%E3%82%A6%E3%82%B9
  // In particular: https://www.youtube.com/watch?v=EEluQ_4eBrs

  'y:PL_eG_ziq86f_JuH3AvfAGi8qv9zn7T_nS', // japanese locking
  'y:PL2LmIWNts41gY1yYQDqh1e4LM4-GbiI-r', // a bunch of individual tutorials, should be split up!
  'y:PLNu-Tjbz985ZgTVzPpMFGpopYbxeLNNWn', // more OGs in here, no real 1/2/3/4/5 though
  'y:PL60B63DCF4C745EF4', // Originality Khan
  'y:PLD3786D9190A031C9', // Includes crap expertvillage as well as japanese ones
];

// VincaniTV (need to make a playlist out of these?):
// - Emiko
// https://www.youtube.com/watch?v=Xc8PmwxVPgY
// https://www.youtube.com/watch?v=6dCIa2vG8f8
// https://www.youtube.com/watch?v=3P55U4_-Q14
// https://www.youtube.com/watch?v=pvx_NzLe7yU
// - Coflo
// https://www.youtube.com/watch?v=ogASj4J77hQ 
// - Jardy
// https://www.youtube.com/watch?v=eVa92XQppTU

// House:
// https://www.youtube.com/watch?v=gTzVvUpQbmM
// https://www.youtube.com/watch?v=ta8htUbPjYQ

// Japanese House:
// https://www.youtube.com/watch?v=hcbDPNg0J9g

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

const defaultTutorials = [
];

async function loadConfig() {
  RemoteConfig.setNamespacedDefaults({
    blogs: JSON.stringify(defaultBlogs),
    tutorials: JSON.stringify(defaultTutorials),
  }, 'Learn');
  await RemoteConfig.fetchWithExpirationDuration(30 * 15);
  await RemoteConfig.activateFetched();
}

loadConfig();

export async function getRemoteBlogs() {
  return JSON.parse(await RemoteConfig.getNamedspacedString('blogs', 'Learn'));
}

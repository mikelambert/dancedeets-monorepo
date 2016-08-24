/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { RemoteConfig } from 'react-native-firebase3';

const defaultTutorials = {
  'House Dance': [
    require('./house/newschool_dictionary.json'),
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
  ],
  'Locking': [
    require('./lock/oldschool_dictionary.json'),
    require('./lock/tonygogo.json'),
    require('./lock/flukey.json'),
    require('./lock/vincanitv.json'),
    require('./lock/japanese.json'),
    require('./lock/yakfilms.json'),
    require('./lock/kenzo.json'),
    require('./lock/ricky.json'),
    require('./lock/russian.json'),
    require('./lock/wordrider.json'),
    require('./lock/panda.json'),
  ],
  'Hip-Hop Dance': [
    require('./hiphop/newschool_dictionary.json'),
    require('./hiphop/alvaro.json'),
    require('./hiphop/moncell.json'),
    require('./hiphop/stezo.json'),
    require('./hiphop/akihico.json'),
    require('./hiphop/vobr.json'),
    require('./hiphop/yakfilms.json'),
    require('./hiphop/miscellaneous.json'),
    require('./hiphop/feelthebounce.json'),
  ],
  'Popping': [
    require('./pop/oakland_boogaloo.json'),
    require('./pop/oldschool_dictionary.json'),
    require('./pop/miscellaneous.json'),
    require('./pop/avex.json'),
    require('./pop/jsmooth_jrock.json'),
    require('./pop/learntopop.json'),
    require('./pop/russian_streetdancetv.json'),
    require('./pop/vincanitv.json'),
    require('./pop/yakfilms.json'),
    require('./pop/salah.json'),
    require('./pop/poppingzone.json'),
    require('./pop/itsmrich.json'),
    require('./pop/jayfunk.json'),
    require('./pop/abm.json'),
    require('./pop/russiantiger.json'),
    require('./pop/japanese.json'),
    require('./pop/jamesbarry.json'),
  ],
  'Waacking': [
    require('./waack/mizuki.json'),
    require('./waack/christina.json'),
    require('./waack/miscellaneous.json'),
  ],
  'Breaking': [
  ],
  'Other': [
    require('./misc/yakfilms.json'),
  ]

};

/*
Locking:
// skeeter and flomaster
  {
    "youtubeId": "P6hwVlKuBU4",
    "duration": "PT15M20S",
    "title": "Old School Dictionary | Poppin', Lockin' & Breakin' | Part 1 HD"
  },
  {
    "youtubeId": "dfHF-kK21Qw",
    "duration": "PT14M8S",
    "title": "Old School Dictionary | Poppin´ ,Lockin´ & Breakin´ | Part 2 HD"
  },
  // Some of these got split up into https://www.youtube.com/user/DrugLock/videos and the end of it...
  Strutting
  Fillmore Style
  Snaking
  Shadow Box
  Puppet Style
  Crazy Legs
  Sleepy Style
  Sneak / Sneaky Peek
  Volkswagon
  Pimp Walk
  Leo Walk
https://www.youtube.com/watch?v=6z5WewBEXi8 skeer rabbits 1-2-3-4

// skeeter and suga pop
  {
    "youtubeId": "ZrzMe-7W8hU",
    "duration": "PT4M50S",
    "title": "Locking Tutorial Compilation with Skeeter Rabbit"
  },

// in a gym
  {
    "youtubeId": "U6TegTeV8kg",
    "duration": "PT4M50S",
    "title": "Skeeter Rabbit : locking tutorial"
  },

  {
    "youtubeId": "bUrX5BoDBrA",
    "duration": "PT6M4S",
    "title": "Popping Tutorial | Skeeter Rabbit | How To Do Walk Out & Variations"
  },
  {
    "youtubeId": "5v9RTdwm72w",
    "duration": "PT1M13S",
    "title": "Scooby Doo | Locking Basics"
  },


// already have, dont need
  {
    "youtubeId": "A7uhR_gC-1c",
    "duration": "PT24M45S",
    "title": "Oldschool_Dictionary Locking.mp4"
  },
  {
    "youtubeId": "W4AfRhzUcY0",
    "duration": "PT15M11S",
    "title": "Oldschool Dictionary part1"
  },

Let's grab these!
https://www.youtube.com/channel/UC7LZQaffoSn2b_ocQg9ATlQ/videos
the animation/tutting video references are still useful?
the wiggles videos too

// popping, but we need to segment or do in-app segmenting:
https://www.youtube.com/watch?v=izngp0yCfyE

// locking chinese
https://www.youtube.com/watch?v=K6TDyBFH5e0
// popping chinese
https://www.youtube.com/watch?v=_-Ergy2XsGg

HipHop:
https://www.youtube.com/channel/UCquj-IS-DKTg-6vRxmwsFbw/videos
https://www.youtube.com/user/streetdanceru/videos
https://www.youtube.com/user/typhoonbroooooooklyn/search?query=tutorial

Gonna ignore:
https://www.youtube.com/channel/UCoU_XspQfZlFy6YC7NEicoQ
*/

const defaultBlogs = [
  'y:PLZelnKT8VJwytJrZY9nmZtslGRdhFaYso', // Jardy in spanish (needs subtitles!)
  'y:PLF5290D54A54C4EDA', // Jardy in Korean (needs subtitles!)
  // Somehow some of these aren't in a playlist? https://www.youtube.com/user/DANCEcoaching/search?query=%E3%83%8F%E3%82%A6%E3%82%B9
  // In particular: https://www.youtube.com/watch?v=EEluQ_4eBrs
];

// Hiphop:
// https://www.youtube.com/watch?v=sPDa5OjHUWY
// https://www.youtube.com/watch?v=eITvtPkm5Lg
// https://www.youtube.com/watch?v=eSCyfUSv38k
// https://www.youtube.com/watch?v=2OK2XbwKamw
// rising school:
// https://www.youtube.com/playlist?list=PLVY6uOsv4D9YoJHuwyA8E7TbbsrPzKfqj
// https://www.youtube.com/playlist?list=PLVY6uOsv4D9ZsP2wTgPaItzrta5AjQiTO
// https://www.youtube.com/user/YAKfilms/search?query=hiphop+tutorial

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

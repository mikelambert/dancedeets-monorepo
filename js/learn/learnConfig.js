/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

export const defaultTutorials = {
  'House Dance': [
    require('./tutorials/house/newschool_dictionary.json'),
    require('./tutorials/house/jardy.json'),
    require('./tutorials/house/rich.json'),
    require('./tutorials/house/malcolm.json'),
    require('./tutorials/house/alvaro.json'),
    require('./tutorials/house/hiro.json'),
    require('./tutorials/house/koji.json'),
    require('./tutorials/house/yeomin.json'),
    require('./tutorials/house/yusuke.json'),
    require('./tutorials/house/vincanitv.json'),
    require('./tutorials/house/japanese.json'),
    require('./tutorials/house/miscellaneous.json'),
  ],
  'Locking': [
    require('./tutorials/lock/oldschool_dictionary.json'),
    require('./tutorials/lock/tonygogo.json'),
    require('./tutorials/lock/flukey.json'),
    require('./tutorials/lock/vincanitv.json'),
    require('./tutorials/lock/japanese.json'),
    require('./tutorials/lock/yakfilms.json'),
    require('./tutorials/lock/kenzo.json'),
    require('./tutorials/lock/ricky.json'),
    require('./tutorials/lock/russian.json'),
    require('./tutorials/lock/wordrider.json'),
    require('./tutorials/lock/panda.json'),
  ],
  'Hip-Hop Dance': [
    require('./tutorials/hiphop/newschool_dictionary.json'),
    require('./tutorials/hiphop/alvaro.json'),
    require('./tutorials/hiphop/moncell.json'),
    require('./tutorials/hiphop/stezo.json'),
    require('./tutorials/hiphop/akihico.json'),
    require('./tutorials/hiphop/vobr.json'),
    require('./tutorials/hiphop/yakfilms.json'),
    require('./tutorials/hiphop/miscellaneous.json'),
    require('./tutorials/hiphop/feelthebounce.json'),
  ],
  'Popping': [
    require('./tutorials/pop/oldschool_dictionary.json'),
    require('./tutorials/pop/skeeterrabbit.json'),
    require('./tutorials/pop/popinpete.json'),
    require('./tutorials/pop/oakland_boogaloo.json'),
    require('./tutorials/pop/wiggles.json'),
    require('./tutorials/pop/miscellaneous.json'),
    require('./tutorials/pop/avex.json'),
    require('./tutorials/pop/jsmooth_jrock.json'),
    require('./tutorials/pop/learntopop.json'),
    require('./tutorials/pop/russian_streetdancetv.json'),
    require('./tutorials/pop/vincanitv.json'),
    require('./tutorials/pop/yakfilms.json'),
    require('./tutorials/pop/salah.json'),
    require('./tutorials/pop/poppingzone.json'),
    require('./tutorials/pop/itsmrich.json'),
    require('./tutorials/pop/jayfunk.json'),
    require('./tutorials/pop/abm.json'),
    require('./tutorials/pop/russiantiger.json'),
    require('./tutorials/pop/dancestylepopping.json'),
    require('./tutorials/pop/dancestylepopping2.json'),
    require('./tutorials/pop/dancestyleanimation.json'),
    require('./tutorials/pop/jamesbarry.json'),
    require('./tutorials/pop/khrys.json'),
    require('./tutorials/pop/mattsteffanina.json'),
    require('./tutorials/pop/baseis.json'),
    require('./tutorials/pop/advice.json'),
    require('./tutorials/pop/korean.json'),
    require('./tutorials/pop/chinese.json'),
    require('./tutorials/pop/umin.json'),
    require('./tutorials/pop/mikesong.json'),
  ],
  'Waacking': [
    require('./tutorials/waack/mizuki.json'),
    require('./tutorials/waack/christina.json'),
    require('./tutorials/waack/miscellaneous.json'),
  ],
  'Breaking': [
    require('./tutorials/break/vincanitv_beginnertutorials.json'),
    require('./tutorials/break/vincanitv_intermediatetutorials.json'),
    require('./tutorials/break/vincanitv_advancedtutorials.json'),
    require('./tutorials/break/vincanitv_toprock basics.json'),
    require('./tutorials/break/vincanitv_getdowns.json'),
    require('./tutorials/break/vincanitv_footwork101.json'),
    require('./tutorials/break/vincanitv_freezebasics.json'),
    require('./tutorials/break/vincanitv_flipbasics.json'),
    require('./tutorials/break/vincanitv_powermoves.json'),
    require('./tutorials/break/vincanitv_flowbasics.json'),
    require('./tutorials/break/vincanitv_stalks.json'),
    require('./tutorials/break/vincanitv_threads.json'),
    require('./tutorials/break/footworkfundamentals.json'),
    require('./tutorials/break/piechienteddie.json'),
    require('./tutorials/break/milestone.json'),
    require('./tutorials/break/roxrite.json'),
    require('./tutorials/break/strifetv.json'),
    require('./tutorials/break/tlil.json'),
    require('./tutorials/break/yakfilms.json'),
    require('./tutorials/break/josef.json'),
    require('./tutorials/break/lprad.json'),
    require('./tutorials/break/pigmie.json'),
    require('./tutorials/break/taisuke.json'),
  ],
  'Urban Choreo / Street Jazz': [
    require('./tutorials/streetjazz/mattsteffanina.json'),
  ],
  'Other': [
    require('./tutorials/misc/yakfilms.json'),
    require('./tutorials/misc/krump.json'),
    require('./tutorials/misc/horie.json'),
    require('./tutorials/misc/riehata.json'),
    require('./tutorials/misc/seto.json'),
    require('./tutorials/misc/kenzo_beginner.json'),
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
https://www.youtube.com/user/typhoonbroooooooklyn/search?query=tutorial

Gonna ignore:
https://www.youtube.com/channel/UCoU_XspQfZlFy6YC7NEicoQ
*/

export const defaultBlogs = [
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
// https://www.youtube.com/user/YAKfilms/search?query=hiphop+tutorial

// Find many here:
// https://www.youtube.com/playlist?list=PLGOtBlWsXfr1eGS2Z2_efsYG3mwpz0WPa
// https://www.youtube.com/user/DANCEdiet/playlists
// https://www.youtube.com/user/WEBDancelesson/playlists
// https://www.youtube.com/user/DANCEcoaching/playlists
// https://www.youtube.com/user/acrobatDANCE/playlists
// https://www.youtube.com/channel/UCAcWPeaHGnvFQvkCmlFK40A/playlists

// Also possibly this one
// https://www.youtube.com/user/ichidancerdesu2/videos

// BBoy:
// https://www.youtube.com/user/LilAznOrginization/videos (3 videos)
// https://www.youtube.com/channel/UCvz5hnbqACYKae6tB9DYbcg/playlists
// https://www.youtube.com/channel/PLVY6uOsv4D9ZsP2wTgPaItzrta5AjQiTO/playlists
// https://www.youtube.com/user/shisou3/playlists

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


/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import styles from '../styles';
import { Playlist } from './models';

/* eslint-disable global-require */
const defaultTutorials = [
  {
    style: styles.break,
    tutorials: [
      require('./playlists/break/vincanitv_beginnertutorials.json'),
      require('./playlists/break/vincanitv_intermediatetutorials.json'),
      require('./playlists/break/vincanitv_advancedtutorials.json'),
      require('./playlists/break/vincanitv_toprock basics.json'),
      require('./playlists/break/vincanitv_getdowns.json'),
      require('./playlists/break/vincanitv_footwork101.json'),
      require('./playlists/break/vincanitv_freezebasics.json'),
      require('./playlists/break/vincanitv_flipbasics.json'),
      require('./playlists/break/vincanitv_powermoves.json'),
      require('./playlists/break/vincanitv_flowbasics.json'),
      require('./playlists/break/vincanitv_stalks.json'),
      require('./playlists/break/vincanitv_threads.json'),
      require('./playlists/break/footworkfundamentals.json'),
      require('./playlists/break/piechienteddie.json'),
      require('./playlists/break/milestone.json'),
      require('./playlists/break/roxrite.json'),
      require('./playlists/break/strifetv.json'),
      require('./playlists/break/tlil.json'),
      require('./playlists/break/yakfilms.json'),
      require('./playlists/break/josef.json'),
      require('./playlists/break/lprad.json'),
      require('./playlists/break/pigmie.json'),
      require('./playlists/break/taisuke.json'),
    ],
  },
  {
    style: styles.hiphop,
    tutorials: [
      require('./playlists/hiphop/nextschool_dictionary.json'),
      require('./playlists/hiphop/newschool_dictionary.json'),
      require('./playlists/hiphop/moncell.json'),
      require('./playlists/hiphop/stezo.json'),
      require('./playlists/hiphop/akihico.json'),
      require('./playlists/hiphop/vobr.json'),
      require('./playlists/hiphop/yakfilms.json'),
      require('./playlists/hiphop/miscellaneous.json'),
      require('./playlists/hiphop/alvaro.json'),
      require('./playlists/hiphop/feelthebounce.json'),
      require('./playlists/hiphop/yesneyes.json'),
    ],
  },
  {
    style: styles.pop,
    tutorials: [
      require('./playlists/pop/oldschool_dictionary.json'),
      require('./playlists/pop/oakland_boogaloo.json'),
      require('./playlists/pop/wiggles.json'),
      require('./playlists/pop/learntopop.json'),
      require('./playlists/pop/miscellaneous.json'),
      require('./playlists/pop/skeeterrabbit.json'),
      require('./playlists/pop/popinpete.json'),
      require('./playlists/pop/avex.json'),
      require('./playlists/pop/jsmooth_jrock.json'),
      require('./playlists/pop/russian_streetdancetv.json'),
      require('./playlists/pop/vincanitv.json'),
      require('./playlists/pop/yakfilms.json'),
      require('./playlists/pop/salah.json'),
      require('./playlists/pop/poppingzone.json'),
      require('./playlists/pop/itsmrich.json'),
      require('./playlists/pop/jayfunk.json'),
      require('./playlists/pop/abm.json'),
      require('./playlists/pop/russiantiger.json'),
      require('./playlists/pop/dancestylepopping.json'),
      require('./playlists/pop/dancestylepopping2.json'),
      require('./playlists/pop/dancestyleanimation.json'),
      require('./playlists/pop/jamesbarry.json'),
      require('./playlists/pop/khrys.json'),
      require('./playlists/pop/mattsteffanina.json'),
      require('./playlists/pop/baseis.json'),
      require('./playlists/pop/advice.json'),
      require('./playlists/pop/korean.json'),
      require('./playlists/pop/chinese.json'),
      require('./playlists/pop/umin.json'),
      require('./playlists/pop/mikesong.json'),
    ],
  },
  {
    style: styles.lock,
    tutorials: [
      require('./playlists/lock/oldschool_dictionary.json'),
      require('./playlists/lock/tonygogo.json'),
      require('./playlists/lock/flukey.json'),
      require('./playlists/lock/vincanitv.json'),
      require('./playlists/lock/japanese.json'),
      require('./playlists/lock/yakfilms.json'),
      require('./playlists/lock/kenzo.json'),
      require('./playlists/lock/ricky.json'),
      require('./playlists/lock/russian.json'),
      require('./playlists/lock/wordrider.json'),
      require('./playlists/lock/panda.json'),
    ],
  },
  {
    style: styles.house,
    tutorials: [
      require('./playlists/house/nextschool_dictionary.json'),
      require('./playlists/house/newschool_dictionary.json'),
      require('./playlists/house/jardy.json'),
      // require('./playlists/house/jardy_footwork.json'),
      // require('./playlists/house/jardy_footwork_expansion.json'),
      require('./playlists/house/rich.json'),
      require('./playlists/house/malcolm.json'),
      require('./playlists/house/alvaro.json'),
      require('./playlists/house/hiro.json'),
      require('./playlists/house/koji.json'),
      require('./playlists/house/yeomin.json'),
      require('./playlists/house/yusuke.json'),
      require('./playlists/house/vincanitv.json'),
      require('./playlists/house/japanese.json'),
      require('./playlists/house/miscellaneous.json'),
    ],
  },
  {
    style: styles.krump,
    tutorials: [
      require('./playlists/krump/krump40.json'),
      require('./playlists/krump/krumpkings.json'),
      require('./playlists/krump/tighteyes.json'),
      require('./playlists/krump/torch.json'),
      require('./playlists/krump/streetdancetv.json'),
      require('./playlists/krump/dancestylekrump.json'),
      require('./playlists/krump/chinese.json'),
    ],
  },
  {
    style: styles.other,
    tutorials: [
      require('./playlists/misc/yakfilms.json'),
      require('./playlists/misc/horie.json'),
      require('./playlists/misc/riehata.json'),
      require('./playlists/misc/seto.json'),
      require('./playlists/waack/kumari.json'),
      require('./playlists/waack/christina.json'),
      require('./playlists/waack/miscellaneous.json'),
      require('./playlists/waack/mizuki.json'),
      require('./playlists/misc/soul_munehiro_sugita.json'),
      require('./playlists/misc/soul_koichi.json'),
      require('./playlists/misc/soul_hakata.json'),
      require('./playlists/misc/soul_so.json'),
      require('./playlists/misc/soul_ricky.json'),
      require('./playlists/streetjazz/mattsteffanina.json'),
      require('./playlists/misc/kenzo_beginner.json'),
      require('./playlists/misc/dancehall_streetdancetv.json'),
      require('./playlists/misc/electro_mitfrol.json'),
      require('./playlists/misc/flex_streetdancetv.json'),
    ],
  },
];
/* eslint-enable global-require */


function sortedTutorials(tutorials, language) {
  const nativeTutorials = [];
  const foreignTutorials = [];
  tutorials.forEach((tut) => {
    if (tut.language === language) {
      nativeTutorials.push(tut);
    } else {
      foreignTutorials.push(tut);
    }
  });
  return [].concat(nativeTutorials, foreignTutorials);
}

export function getTutorials() {
  const constructedPlaylists = defaultTutorials.map(style => ({
    ...style,
    tutorials: sortedTutorials(style.tutorials, this.props.intl.locale).map(x => new Playlist(x)),
  }));
  return constructedPlaylists;
}
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

    {
      "title": "English of Japanese Dancers Box Step",
      "videos": [
        {
          "youtubeId": "rFVml6p3P64",
          "duration": "PT3M51S",
          "title": "Unknown Dancers",
          "height": 344,
          "width": 459
        }
      ]
    },

https://www.youtube.com/user/ilovethisdance/search?query=tutorial

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


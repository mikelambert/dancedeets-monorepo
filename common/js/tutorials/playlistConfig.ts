/**
 * Copyright 2016 DanceDeets.
 */

import styles, { Style } from '../styles';
import { Playlist } from './models';

export interface Category {
  style: Style;
  tutorials: Array<Playlist>;
}

interface PlaylistJson {
  id: string;
  title: string;
  subtitle: string;
  keywords: string;
  author: string;
  style: string;
  language: string;
  thumbnail: string;
  sections: Array<{
    title: string;
    videos: Array<{
      title: string;
      duration: number;
      youtubeId: string;
      width: number;
      height: number;
      keywords?: string[];
    }>;
  }>;
}

interface RawCategory {
  style: Style;
  tutorials: PlaylistJson[];
}

/* eslint-disable global-require, @typescript-eslint/no-var-requires */
const defaultTutorials: RawCategory[] = [
  {
    style: styles.break,
    tutorials: [
      require('./playlists/break/vincanitv_beginner.json'),
      require('./playlists/break/vincanitv_intermediate.json'),
      require('./playlists/break/vincanitv_advanced.json'),
      require('./playlists/break/vincanitv_toprock.json'),
      require('./playlists/break/vincanitv_getdowns.json'),
      require('./playlists/break/vincanitv_footwork.json'),
      require('./playlists/break/vincanitv_freezes.json'),
      require('./playlists/break/vincanitv_flips.json'),
      require('./playlists/break/vincanitv_power.json'),
      require('./playlists/break/vincanitv_flow.json'),
      require('./playlists/break/vincanitv_stalks.json'),
      require('./playlists/break/vincanitv_threads.json'),
      require('./playlists/break/footworkfundamentals.json'),
      require('./playlists/break/darrenwong.json'),
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
      require('./playlists/waack/lion_cho.json'),
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
/* eslint-enable global-require, @typescript-eslint/no-var-requires */

function sortedTutorials(
  tutorials: PlaylistJson[],
  locale: string
): PlaylistJson[] {
  const nativeTutorials: PlaylistJson[] = [];
  const foreignTutorials: PlaylistJson[] = [];
  const language = locale.split('-')[0];
  tutorials.forEach(tut => {
    if (tut.language === language) {
      nativeTutorials.push(tut);
    } else {
      foreignTutorials.push(tut);
    }
  });
  return ([] as PlaylistJson[]).concat(nativeTutorials, foreignTutorials);
}

export function getTutorials(locale: string): Array<Category> {
  const constructedPlaylists = defaultTutorials.map(style => ({
    ...style,
    tutorials: sortedTutorials(style.tutorials, locale).map(
      x => new Playlist(x)
    ),
  }));
  return constructedPlaylists;
}

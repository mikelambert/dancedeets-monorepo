/**
 * Copyright 2016 DanceDeets.
 */

import styles, { Style } from '../styles';
import { Playlist, PlaylistJson } from './models';

// Break playlists
import vincanitv_beginner from './playlists/break/vincanitv_beginner.json';
import vincanitv_intermediate from './playlists/break/vincanitv_intermediate.json';
import vincanitv_advanced from './playlists/break/vincanitv_advanced.json';
import vincanitv_toprock from './playlists/break/vincanitv_toprock.json';
import vincanitv_getdowns from './playlists/break/vincanitv_getdowns.json';
import vincanitv_footwork from './playlists/break/vincanitv_footwork.json';
import vincanitv_freezes from './playlists/break/vincanitv_freezes.json';
import vincanitv_flips from './playlists/break/vincanitv_flips.json';
import vincanitv_power from './playlists/break/vincanitv_power.json';
import vincanitv_flow from './playlists/break/vincanitv_flow.json';
import vincanitv_stalks from './playlists/break/vincanitv_stalks.json';
import vincanitv_threads from './playlists/break/vincanitv_threads.json';
import footworkfundamentals from './playlists/break/footworkfundamentals.json';
import darrenwong from './playlists/break/darrenwong.json';
import piechienteddie from './playlists/break/piechienteddie.json';
import milestone from './playlists/break/milestone.json';
import roxrite from './playlists/break/roxrite.json';
import strifetv from './playlists/break/strifetv.json';
import tlil from './playlists/break/tlil.json';
import break_yakfilms from './playlists/break/yakfilms.json';
import josef from './playlists/break/josef.json';
import lprad from './playlists/break/lprad.json';
import pigmie from './playlists/break/pigmie.json';
import taisuke from './playlists/break/taisuke.json';

// HipHop playlists
import hiphop_nextschool_dictionary from './playlists/hiphop/nextschool_dictionary.json';
import hiphop_newschool_dictionary from './playlists/hiphop/newschool_dictionary.json';
import moncell from './playlists/hiphop/moncell.json';
import stezo from './playlists/hiphop/stezo.json';
import akihico from './playlists/hiphop/akihico.json';
import vobr from './playlists/hiphop/vobr.json';
import hiphop_yakfilms from './playlists/hiphop/yakfilms.json';
import hiphop_miscellaneous from './playlists/hiphop/miscellaneous.json';
import hiphop_alvaro from './playlists/hiphop/alvaro.json';
import feelthebounce from './playlists/hiphop/feelthebounce.json';
import yesneyes from './playlists/hiphop/yesneyes.json';

// Pop playlists
import oldschool_dictionary from './playlists/pop/oldschool_dictionary.json';
import oakland_boogaloo from './playlists/pop/oakland_boogaloo.json';
import wiggles from './playlists/pop/wiggles.json';
import learntopop from './playlists/pop/learntopop.json';
import pop_miscellaneous from './playlists/pop/miscellaneous.json';
import skeeterrabbit from './playlists/pop/skeeterrabbit.json';
import popinpete from './playlists/pop/popinpete.json';
import avex from './playlists/pop/avex.json';
import jsmooth_jrock from './playlists/pop/jsmooth_jrock.json';
import russian_streetdancetv from './playlists/pop/russian_streetdancetv.json';
import pop_vincanitv from './playlists/pop/vincanitv.json';
import pop_yakfilms from './playlists/pop/yakfilms.json';
import salah from './playlists/pop/salah.json';
import poppingzone from './playlists/pop/poppingzone.json';
import itsmrich from './playlists/pop/itsmrich.json';
import jayfunk from './playlists/pop/jayfunk.json';
import abm from './playlists/pop/abm.json';
import russiantiger from './playlists/pop/russiantiger.json';
import dancestylepopping from './playlists/pop/dancestylepopping.json';
import dancestylepopping2 from './playlists/pop/dancestylepopping2.json';
import dancestyleanimation from './playlists/pop/dancestyleanimation.json';
import jamesbarry from './playlists/pop/jamesbarry.json';
import khrys from './playlists/pop/khrys.json';
import pop_mattsteffanina from './playlists/pop/mattsteffanina.json';
import baseis from './playlists/pop/baseis.json';
import advice from './playlists/pop/advice.json';
import korean from './playlists/pop/korean.json';
import pop_chinese from './playlists/pop/chinese.json';
import umin from './playlists/pop/umin.json';
import mikesong from './playlists/pop/mikesong.json';

// Lock playlists
import lock_oldschool_dictionary from './playlists/lock/oldschool_dictionary.json';
import tonygogo from './playlists/lock/tonygogo.json';
import flukey from './playlists/lock/flukey.json';
import lock_vincanitv from './playlists/lock/vincanitv.json';
import lock_japanese from './playlists/lock/japanese.json';
import lock_yakfilms from './playlists/lock/yakfilms.json';
import kenzo from './playlists/lock/kenzo.json';
import ricky from './playlists/lock/ricky.json';
import russian from './playlists/lock/russian.json';
import wordrider from './playlists/lock/wordrider.json';
import panda from './playlists/lock/panda.json';

// House playlists
import house_nextschool_dictionary from './playlists/house/nextschool_dictionary.json';
import house_newschool_dictionary from './playlists/house/newschool_dictionary.json';
import jardy from './playlists/house/jardy.json';
import rich from './playlists/house/rich.json';
import malcolm from './playlists/house/malcolm.json';
import house_alvaro from './playlists/house/alvaro.json';
import hiro from './playlists/house/hiro.json';
import koji from './playlists/house/koji.json';
import yeomin from './playlists/house/yeomin.json';
import yusuke from './playlists/house/yusuke.json';
import house_vincanitv from './playlists/house/vincanitv.json';
import house_japanese from './playlists/house/japanese.json';
import house_miscellaneous from './playlists/house/miscellaneous.json';

// Krump playlists
import krump40 from './playlists/krump/krump40.json';
import krumpkings from './playlists/krump/krumpkings.json';
import tighteyes from './playlists/krump/tighteyes.json';
import torch from './playlists/krump/torch.json';
import krump_streetdancetv from './playlists/krump/streetdancetv.json';
import dancestylekrump from './playlists/krump/dancestylekrump.json';
import krump_chinese from './playlists/krump/chinese.json';

// Misc playlists
import misc_yakfilms from './playlists/misc/yakfilms.json';
import horie from './playlists/misc/horie.json';
import riehata from './playlists/misc/riehata.json';
import seto from './playlists/misc/seto.json';
import kumari from './playlists/waack/kumari.json';
import lion_cho from './playlists/waack/lion_cho.json';
import christina from './playlists/waack/christina.json';
import waack_miscellaneous from './playlists/waack/miscellaneous.json';
import mizuki from './playlists/waack/mizuki.json';
import soul_munehiro_sugita from './playlists/misc/soul_munehiro_sugita.json';
import soul_koichi from './playlists/misc/soul_koichi.json';
import soul_hakata from './playlists/misc/soul_hakata.json';
import soul_so from './playlists/misc/soul_so.json';
import soul_ricky from './playlists/misc/soul_ricky.json';
import streetjazz_mattsteffanina from './playlists/streetjazz/mattsteffanina.json';
import kenzo_beginner from './playlists/misc/kenzo_beginner.json';
import dancehall_streetdancetv from './playlists/misc/dancehall_streetdancetv.json';
import electro_mitfrol from './playlists/misc/electro_mitfrol.json';
import flex_streetdancetv from './playlists/misc/flex_streetdancetv.json';

export interface Category {
  style: Style;
  tutorials: Array<Playlist>;
}

interface RawCategory {
  style: Style;
  tutorials: PlaylistJson[];
}

const defaultTutorials: RawCategory[] = [
  {
    style: styles.break,
    tutorials: [
      vincanitv_beginner,
      vincanitv_intermediate,
      vincanitv_advanced,
      vincanitv_toprock,
      vincanitv_getdowns,
      vincanitv_footwork,
      vincanitv_freezes,
      vincanitv_flips,
      vincanitv_power,
      vincanitv_flow,
      vincanitv_stalks,
      vincanitv_threads,
      footworkfundamentals,
      darrenwong,
      piechienteddie,
      milestone,
      roxrite,
      strifetv,
      tlil,
      break_yakfilms,
      josef,
      lprad,
      pigmie,
      taisuke,
    ] as PlaylistJson[],
  },
  {
    style: styles.hiphop,
    tutorials: [
      hiphop_nextschool_dictionary,
      hiphop_newschool_dictionary,
      moncell,
      stezo,
      akihico,
      vobr,
      hiphop_yakfilms,
      hiphop_miscellaneous,
      hiphop_alvaro,
      feelthebounce,
      yesneyes,
    ] as PlaylistJson[],
  },
  {
    style: styles.pop,
    tutorials: [
      oldschool_dictionary,
      oakland_boogaloo,
      wiggles,
      learntopop,
      pop_miscellaneous,
      skeeterrabbit,
      popinpete,
      avex,
      jsmooth_jrock,
      russian_streetdancetv,
      pop_vincanitv,
      pop_yakfilms,
      salah,
      poppingzone,
      itsmrich,
      jayfunk,
      abm,
      russiantiger,
      dancestylepopping,
      dancestylepopping2,
      dancestyleanimation,
      jamesbarry,
      khrys,
      pop_mattsteffanina,
      baseis,
      advice,
      korean,
      pop_chinese,
      umin,
      mikesong,
    ] as PlaylistJson[],
  },
  {
    style: styles.lock,
    tutorials: [
      lock_oldschool_dictionary,
      tonygogo,
      flukey,
      lock_vincanitv,
      lock_japanese,
      lock_yakfilms,
      kenzo,
      ricky,
      russian,
      wordrider,
      panda,
    ] as PlaylistJson[],
  },
  {
    style: styles.house,
    tutorials: [
      house_nextschool_dictionary,
      house_newschool_dictionary,
      jardy,
      rich,
      malcolm,
      house_alvaro,
      hiro,
      koji,
      yeomin,
      yusuke,
      house_vincanitv,
      house_japanese,
      house_miscellaneous,
    ] as PlaylistJson[],
  },
  {
    style: styles.krump,
    tutorials: [
      krump40,
      krumpkings,
      tighteyes,
      torch,
      krump_streetdancetv,
      dancestylekrump,
      krump_chinese,
    ] as PlaylistJson[],
  },
  {
    style: styles.other,
    tutorials: [
      misc_yakfilms,
      horie,
      riehata,
      seto,
      kumari,
      lion_cho,
      christina,
      waack_miscellaneous,
      mizuki,
      soul_munehiro_sugita,
      soul_koichi,
      soul_hakata,
      soul_so,
      soul_ricky,
      streetjazz_mattsteffanina,
      kenzo_beginner,
      dancehall_streetdancetv,
      electro_mitfrol,
      flex_streetdancetv,
    ] as PlaylistJson[],
  },
];

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

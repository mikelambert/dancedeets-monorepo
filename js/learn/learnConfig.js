/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import { RemoteConfig } from 'react-native-firebase3';

const defaultBlogs = [
  'y:PLB9CAA2877007AC02', // Jardy: basic
  'y:PLE839D54D07A8ABC2', // Jardy: advanced
];
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

/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';
import fetch from 'node-fetch';
import * as fs from 'fs';
import {
  YoutubeKey,
  getUrl,
  loadPlaylist,
} from './fetchYoutubeVideosCore.js';

async function loadPlaylistData(playlistIds) {
  const playlistUrl = getUrl('https://www.googleapis.com/youtube/v3/playlists',
  {
    id: playlistIds.join(','),
    part: 'snippet',
    key: YoutubeKey,
  });
  const playlistJson = await (await fetch(playlistUrl)).json();
  return playlistJson;
}

function transformTitle(title) {
  const toTrim = [
  ' | Beginner\'s Guide',
  ' | Beginners Guide',
  ' | Power Move Basics',
  ' | Top Rock Basics',
  ' | Footwork 101',
  ' | Flow Basics',
  ' | Freeze Basics',
  'How to Breakdance | ',
  'How to ',
  ];
  let newTitle = title;
  toTrim.forEach((x) => {
    newTitle = newTitle.replace(x, '');
  });
  return newTitle;
}

async function reloadPlaylists(playlistIds) {
  const playlistsJson = await loadPlaylistData(playlistIds);
  for (const playlist of playlistsJson.items) {
    const playlistTitle = playlist.snippet.title.replace('How to Breakdance | ', '');
    console.log(playlistTitle);
    const tutorialItemsJson = await loadPlaylist(playlist.id);
    tutorialItemsJson.forEach((x) => {
      x.title = transformTitle(x.title);
    });
    const tutorial = {
      title: `VincaniTV - ${playlistTitle}`,
      author: 'VincaniTV Teachers',
      style: 'break',
      language: 'en',
      thumbnail: playlist.snippet.thumbnails.standard.url,
      sections: [
        {
          title: 'Tutorials',
          videos: tutorialItemsJson,
        }
      ],
    };
    const filename = `./js/learn/break/vincanitv_${playlistTitle.replace(' ', '').toLowerCase()}.json`;
    fs.writeFile(filename, JSON.stringify(tutorial, null, '  '));
  }
}

const playlists = {
  'Beginner Tutorials': 'PLXNyOoexGdSfSCuOyqNGmvbFC4BhtuB2s',
  'Intermediate Tutorials': 'PLXNyOoexGdSdNRVaw6Mxiw2TuW6a3qsIW',
  'Toprock Basics': 'PL57E01028C82367BD',
  'Power Moves': 'PL0498871864379CC0',
  'Footwork 101': 'PLC03D627286ADDD94',
  'Flow Basics': 'PLAC0D471C896905D0',
  'Get Downs': 'PL0DEB8E2F99580688',
  'Freeze Basics': 'PL667C395494400FC0',
  'Stalks': 'PLXNyOoexGdSfQO1D9jDK7c1PdfcfX5QgM',
  'Advanced Tutorials': 'PLXNyOoexGdScpZm5Lz34vqXPCFAtgYGtH',
  'Threads': 'PLXNyOoexGdSdcDfwiWDvuDygzaOyPws_1',
  'Flip Basics': 'PL8241BE901CCB9802',
};

reloadPlaylists(Object.values(playlists));

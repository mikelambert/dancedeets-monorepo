#!/usr/bin/awk BEGIN{a=b=ARGV[1];sub(/[A-Za-z_.]+$/,"../../runNode.js",a);sub(/^.*\//,"./",b);system(a"\t"b)}

/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
import fetch from 'node-fetch';
import * as fs from 'fs';
import zip from 'lodash/zip';
import { loadPlaylist } from './fetchYoutubeVideos';
import { findVideoDimensions, getUrl, YoutubeKey } from './_youtube';

async function loadPlaylistData(playlistIds) {
  const playlistUrl = getUrl(
    'https://www.googleapis.com/youtube/v3/playlists',
    {
      id: playlistIds.join(','),
      part: 'snippet',
      key: YoutubeKey,
    }
  );
  const playlistJson = await (await fetch(playlistUrl)).json();
  return playlistJson;
}

function transformTitle(title) {
  const toTrim = [
    " | Beginner's Guide",
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
  toTrim.forEach(x => {
    newTitle = newTitle.replace(x, '');
  });
  return newTitle;
}

type PlaylistInfo = {
  id: string,
  name: string,
  playlist: string,
};

async function reloadPlaylists(playlistInfos: Array<PlaylistInfo>) {
  const playlistsJson = await loadPlaylistData(
    playlistInfos.map(x => x.playlist)
  );
  for (const playlist of playlistsJson.items) {
    const playlistInfo = playlistInfos.filter(
      x => x.playlist === playlist.id
    )[0];

    console.log(playlistInfo.name);

    const tutorialItemsJson = await loadPlaylist(playlist.id);
    const videoDimensions = await findVideoDimensions(
      tutorialItemsJson.map(x => x.youtubeId)
    );
    const tempTutorialItems = tutorialItemsJson.map(x => ({
      ...x,
      title: transformTitle(x.title),
      ...videoDimensions[x.youtubeId],
    }));
    // De-dupe the array on ids, keeping only the first element (where pos == found-itself)
    const finalTutorialItems = tempTutorialItems.filter((item, pos, self) => {
      return self.findIndex(x => x.id == item.id) == pos;
    });
    const tutorial = {
      id: playlistInfo.id,
      title: `VincaniTV: ${playlistInfo.name}`,
      author: 'VincaniTV Teachers',
      style: 'break',
      language: 'en',
      thumbnail: playlist.snippet.thumbnails.standard.url.replace(
        'sddefault',
        'mqdefault'
      ),
      sections: [
        {
          title: 'Tutorials',
          videos: finalTutorialItems,
        },
      ],
    };
    const filename = `../js/tutorials/playlists/break/${playlistInfo.id.replace(
      '-',
      '_'
    )}.json`;
    fs.writeFile(filename, JSON.stringify(tutorial, null, '  '));
  }
}

const playlists = [
  {
    id: 'vincanitv-beginner',
    name: 'Beginner',
    playlist: 'PLXNyOoexGdSfSCuOyqNGmvbFC4BhtuB2s',
  },
  {
    id: 'vincanitv-intermediate',
    name: 'Intermediate',
    playlist: 'PLXNyOoexGdSdNRVaw6Mxiw2TuW6a3qsIW',
  },
  {
    id: 'vincanitv-toprock',
    name: 'Toprock',
    playlist: 'PL57E01028C82367BD',
  },
  {
    id: 'vincanitv-power',
    name: 'Power Moves',
    playlist: 'PL0498871864379CC0',
  },
  {
    id: 'vincanitv-footwork',
    name: 'Footwork',
    playlist: 'PLC03D627286ADDD94',
  },
  {
    id: 'vincanitv-flow',
    name: 'Flow',
    playlist: 'PLAC0D471C896905D0',
  },
  {
    id: 'vincanitv-getdowns',
    name: 'Getdowns',
    playlist: 'PL0DEB8E2F99580688',
  },
  {
    id: 'vincanitv-freezes',
    name: 'Freezes',
    playlist: 'PL667C395494400FC0',
  },
  {
    id: 'vincanitv-stalks',
    name: 'Stalks',
    playlist: 'PLXNyOoexGdSfQO1D9jDK7c1PdfcfX5QgM',
  },
  {
    id: 'vincanitv-advanced',
    name: 'Advanced',
    playlist: 'PLXNyOoexGdScpZm5Lz34vqXPCFAtgYGtH',
  },
  {
    id: 'vincanitv-threads',
    name: 'Threads',
    playlist: 'PLXNyOoexGdSdcDfwiWDvuDygzaOyPws_1',
  },
  {
    id: 'vincanitv-flips',
    name: 'Flips',
    playlist: 'PL8241BE901CCB9802',
  },
];

reloadPlaylists(playlists);

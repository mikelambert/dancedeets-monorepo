/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import fetch from 'node-fetch';

export async function findVideoDimensions(videoIds: Array<string>) {
  const dimensions = {};
  for (const videoId of videoIds) {
    const oEmbedUrl = `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`;
    try {
      const results = await (await fetch(oEmbedUrl)).json();
      dimensions[videoId] = {width: results.width, height: results.height};
    } catch (err) {
      console.error(oEmbedUrl, err);
    }
  }
  return dimensions;
}
/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import fetch from 'node-fetch';
import querystring from 'querystring';

export const YoutubeKey = 'AIzaSyCV8QCRxSwv1vVk017qI3EZ9zlC8TefUjY';

export function getUrl(path: string, args: Object) {
  const formattedArgs = querystring.stringify(args);
  let fullPath = path;
  if (formattedArgs) {
    fullPath += `?${formattedArgs}`;
  }
  return fullPath;
}

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

export async function fetchAll(pageUrl: string, pageToken?: string) {
  const newUrl = pageUrl + (pageToken ? `&pageToken=${pageToken}` : '');
  const pageJson = await (await fetch(newUrl)).json();
  if (pageJson.nextPageToken) {
    const pageJson2 = await fetchAll(pageUrl, pageJson.nextPageToken);
    Array.prototype.push.apply(pageJson.items, pageJson2.items);
  }
  return pageJson;
}


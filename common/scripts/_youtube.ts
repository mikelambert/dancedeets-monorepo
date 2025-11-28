/**
 * Copyright 2016 DanceDeets.
 */

import fetch from 'node-fetch';
import querystring from 'querystring';

export const YoutubeKey = 'AIzaSyCV8QCRxSwv1vVk017qI3EZ9zlC8TefUjY';

export function getUrl(path: string, args: Record<string, any>): string {
  const formattedArgs = querystring.stringify(args);
  let fullPath = path;
  if (formattedArgs) {
    fullPath += `?${formattedArgs}`;
  }
  return fullPath;
}

export interface VideoDimensions {
  width: number;
  height: number;
}

export async function findVideoDimensions(videoIds: string[]): Promise<Record<string, VideoDimensions>> {
  const dimensions: Record<string, VideoDimensions> = {};
  for (const videoId of videoIds) {
    const oEmbedUrl = `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`;
    try {
      const results = await (await fetch(oEmbedUrl)).json();
      dimensions[videoId] = { width: results.width, height: results.height };
    } catch (err) {
      console.error(oEmbedUrl, err);
    }
  }
  return dimensions;
}

export interface PageJson {
  items: any[];
  nextPageToken?: string;
}

export async function fetchAll(pageUrl: string, pageToken?: string): Promise<PageJson> {
  const newUrl = pageUrl + (pageToken ? `&pageToken=${pageToken}` : '');
  const pageJson: PageJson = await (await fetch(newUrl)).json();
  if (pageJson.nextPageToken) {
    const pageJson2 = await fetchAll(pageUrl, pageJson.nextPageToken);
    Array.prototype.push.apply(pageJson.items, pageJson2.items);
  }
  return pageJson;
}

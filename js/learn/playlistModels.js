/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';

import moment from 'moment';

export class Playlist {
  title: string;
  subtitle: string;
  author: string;
  style: string;
  language: string;
  thumbnail: string;
  sections: [Section];

  constructor(json: any) {
    this.title = json.title;
    this.subtitle = json.subtitle;
    this.author = json.author;
    this.style = json.style;
    this.language = json.language;
    this.thumbnail = json.thumbnail;
    this.sections = json.sections.map((x) => new Section(x));
  }
  getDurationSeconds(): number {
    return this.sections.reduce((reduced, item) => reduced + item.getDurationSeconds(), 0);
  }

  getItems(selectedIndex: number) {
    const selectedVideo = this.getVideo(selectedIndex);
    const items = {};
    this.sections.forEach((section, i) => {
      items[section.key(i)] = section.videos.map((video) => ({video, selected: video == selectedVideo}));
    });
    return items;
  }

  getSectionHeaders() {
    return this.sections.map((x, i) => x.key(i));
  }

  getVideo(index: number) {
    const originalIndex = index;
    for (var i = 0; i < this.sections.length; i++) {
      const section = this.sections[i];
      if (index < section.videos.length) {
        return section.videos[index];
      } else {
        index -= section.videos.length;
      }
    }
    console.error(`Video index out of range: ${originalIndex}`);
  }

  getVideoIndex(video: Video) {
    let index = 0;
    for (var i = 0; i < this.sections.length; i++) {
      const videos = this.sections[i].videos;
      const sectionIndex = videos.indexOf(video);
      if (sectionIndex > -1) {
        return index + sectionIndex;
      } else {
        index += videos.length;
      }
    }
    console.error('Video not in tutorial for index lookup');
  }

  getVideoCount() {
    let count = 0;
    for (var i = 0; i < this.sections.length; i++) {
      count += this.sections[i].videos.length;
    }
    return count;
  }
}

export class Section {
  title: string;
  videos: [Video];

  constructor(json: any) {
    try {
      this.title = json.title;
      this.videos = json.videos.map((x) => new Video(x));
    } catch (e) {
      console.log('Error on playlist: ', json);
      throw e;
    }
  }

  getDurationSeconds(): number {
    return this.videos.reduce((reduced, item) => reduced + item.getDurationSeconds(), 0);
  }

  key(index: number) {
    return JSON.stringify({
      index: index,
      title: this.title,
      durationSeconds: this.getDurationSeconds(),
    });
  }
}

export class Video {
  title: string;
  duration: number;
  url: string;
  youtubeId: string;
  width: number;
  height: number;

  constructor(json: any) {
    try {
      this.title = json.title;
      this.duration = json.duration;
      this.youtubeId = json.youtubeId;
      this.width = json.width;
      this.height = json.height;
    } catch (e) {
      console.log('Error on video: ', json);
      throw e;
    }
  }

  getDurationSeconds(): number {
    return moment.duration(this.duration).asSeconds();
  }
}

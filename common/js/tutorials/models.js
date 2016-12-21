/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import moment from 'moment';

import type {
  messageDescriptorPropTypes,
} from 'react-intl/src/types';


export class Playlist {
  id: string;
  title: string;
  subtitle: string;
  author: string;
  style: string;
  language: string;
  thumbnail: string;
  sections: Section[];

  constructor(json: any) {
    this.id = json.id;
    this.title = json.title;
    this.subtitle = json.subtitle;
    this.author = json.author;
    this.style = json.style;
    this.language = json.language;
    this.thumbnail = json.thumbnail;
    this.sections = json.sections.map(x => new Section(x));
  }

  getDurationSeconds(): number {
    return this.sections.reduce((reduced, item) => reduced + item.getDurationSeconds(), 0);
  }

  getId() {
    return `${this.style}/${this.id}`;
  }

  getUrl() {
    return `http://www.dancedeets.com/tutorials/${this.getId()}`;
  }

  getItems(selectedIndex: number) {
    const selectedVideo = this.getVideo(selectedIndex);
    const items = {};
    this.sections.forEach((section, i) => {
      items[section.key(i)] = section.videos.map(video => ({ video, selected: video === selectedVideo }));
    });
    return items;
  }

  getSectionHeaders() {
    return this.sections.map((x, i) => x.key(i));
  }

  getVideo(index: number): Video {
    let currentIndex = index;
    const originalIndex = index;
    for (let i = 0; i < this.sections.length; i += 1) {
      const section = this.sections[i];
      if (currentIndex < section.videos.length) {
        return section.videos[currentIndex];
      } else {
        currentIndex -= section.videos.length;
      }
    }
    throw new Error(`Video index out of range: ${originalIndex}`);
  }

  getVideoIndex(video: Video): number {
    let index = 0;
    for (let i = 0; i < this.sections.length; i += 1) {
      const videos = this.sections[i].videos;
      const sectionIndex = videos.findIndex(thisVideo => thisVideo.youtubeId === video.youtubeId);
      if (sectionIndex > -1) {
        return index + sectionIndex;
      } else {
        index += videos.length;
      }
    }
    throw new Error('Video not in tutorial for index lookup');
  }

  getVideoSectionRow(index: number): {section: number, row: number} {
    let currentIndex = index;
    const originalIndex = index;
    for (let i = 0; i < this.sections.length; i += 1) {
      const section = this.sections[i];
      if (currentIndex < section.videos.length) {
        return { section: i, row: currentIndex };
      } else {
        currentIndex -= section.videos.length;
      }
    }
    throw new Error(`Video index out of range: ${originalIndex}`);
  }

  getVideoCount() {
    let count = 0;
    for (let i = 0; i < this.sections.length; i += 1) {
      count += this.sections[i].videos.length;
    }
    return count;
  }

  // Generate a bunch of text contained by this tutorial, for searching purposes
  getFullText() {
    const textBits = [];
    textBits.push(this.title);
    textBits.push(this.subtitle);
    textBits.push(this.author);
    textBits.push(this.style);
    textBits.push(this.style);
    this.sections.forEach((section) => {
      textBits.push(section.title);
      section.videos.forEach((video) => {
        textBits.push(video.title);
      });
    });
    return textBits.join(' ');
  }
}

export class Section {
  title: string;
  videos: Video[];

  constructor(json: any) {
    try {
      this.title = json.title;
      this.videos = json.videos.map(x => new Video(x));
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
      index,
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

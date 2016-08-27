
export class Tutorial {
  title: string;
  description: string;
  author: string;
  style: string;
  language: string;
  thumbnail: string;
  sections: [Section];

  constructor(json: any) {
    this.title = json.title;
    this.description = json.description;
    this.author = json.author;
    this.style = json.style;
    this.language = json.language;
    this.thumbnail = json.thumbnail;
    this.sections = json.sections.map((x) => new Section(x));
  }
  getDurationSeconds(): number {
    return this.sections.reduce((reduced, item) => reduced + item.getDurationSeconds(), 0);
  }

  getItems() {
    const items = {};
    this.sections.forEach((x, i) => {
      items[x.key(i)] = x.videos;
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
}

export class Section {
  title: string;
  videos: [Video];

  constructor(json: any) {
    this.title = json.title;
    this.videos = json.videos.map((x) => new Video(x));
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

  constructor(json: any) {
    this.title = json.title;
    this.duration = json.duration;
    this.youtubeId = json.youtubeId;
  }

  getDurationSeconds(): number {
    return moment.duration(this.duration).asSeconds();
  }
}
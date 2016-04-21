/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

type JSON = | string | number | boolean | null | JSONObject | JSONArray;
type JSONObject = { [key:string]: JSON };
type JSONArray = Array<JSON>;

export class Event extends Object {
  id: string;
  city: string;
  country: string;
  venue: string;
  picture: string;
  name: string;
  start_time: Date;
  end_time: Date;
  annotations: {categories: Array<string>};

  constructor(eventData: JSONObject) {
    super();
    for (var attr in eventData) {
      if (eventData.hasOwnProperty(attr)) {
        (this: any)[attr] = eventData[attr];
      }
    }
    return this;
  }

  getImageProps() {
    var url = this.picture;
    var width = 100;
    var height = 100;
    if (this.cover !== null && this.cover.images.length > 0) {
      var image = this.cover.images[0];
      url = image.source;
      width = image.width;
      height = image.height;
    }
    return {url, width, height};
  }
}

class Event {
  constructor(eventData) {
    for (var attr in eventData) {
      if (eventData.hasOwnProperty(attr)) {
        this[attr] = eventData[attr];
      }
    }
    return this;
  }

  getImageProps() {
    var url = this.picture;
    var width = 100;
    var height = 100;
    if (this.cover != null && this.cover.images.length > 0) {
      var image = this.cover.images[0];
      url = image.source;
      width = image.width;
      height = image.height;
    }
    return {url, width, height};
  }

}

module.exports = {
    Event,
}
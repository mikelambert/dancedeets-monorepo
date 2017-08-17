/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import Linkify from 'linkify-it';
import tlds from 'tlds';
import url from 'url';

const linkify = Linkify();
linkify.tlds(tlds);

class Formatter {
  str: string;
  options: Object;
  elements: Array<React$Element<*> | string>;

  constructor(str, options) {
    this.str = str;
    this.options = options;
    this.elements = [];

    this.reformat();
  }

  reformat() {
    const matches = linkify.match(this.str) || [];
    let index = 0;

    matches.forEach((match, i) => {
      const part = this.str.slice(index, match.index);

      index = match.lastIndex;

      this.splitNewlines(part, i);
      this.replaceLink(match, i);
    });

    this.splitNewlines(this.str.slice(index), matches.length);
  }

  splitNewlines(str, i) {
    const parts = str.split(/\n|\r/);

    parts.forEach((part, j) => {
      if (part) {
        this.elements.push(part);
      }
      if (j < parts.length - 1) {
        this.elements.push(<br key={`${i}.${j}`} />);
      }
    });
  }

  replaceLink(match, i) {
    let target = this.options.target;
    if (target !== undefined) {
      target = /^http(s)?:/.test(match.url) ? '_blank' : null;
    }
    let rel = this.options.rel;
    if (rel !== undefined) {
      rel = target === '_blank' ? 'noopener noreferrer' : null;
    }

    const parsedUrl = url.parse(match.url, true);
    console.log(parsedUrl);
    if (
      parsedUrl.host === 'www.youtube.com' &&
      parsedUrl.pathname === '/watch' &&
      parsedUrl.query &&
      parsedUrl.query.v
    ) {
      const videoId = parsedUrl.query.v;
      this.elements.push(
        <div key={i} className="video-container">
          <iframe
            id="ytplayer"
            type="text/html"
            width="640"
            height="360"
            src={`https://www.youtube.com/embed/${videoId}`}
            frameBorder="0"
          />
        </div>
      );
    } else {
      this.elements.push(
        <a key={i} target={target} rel={rel} href={match.url}>{match.text}</a>
      );
    }
  }
}

export default class DescriptionFormatter extends React.Component {
  props: {
    children: string,
  };

  render() {
    const text = this.props.children;
    const formatter = new Formatter(text, this.props);
    return <span>{formatter.elements}</span>;
  }
}

/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';
import Linkify from 'linkify-it';
import tlds from 'tlds';
import url from 'url';
import FBPage from 'facebook-plugins/lib/FBPage';
import querystring from 'querystring';
import Helmet from 'react-helmet';

const linkify = Linkify();
linkify.tlds(tlds);

class SoundCloud extends React.Component {
  props: {
    url: string,
  };

  state: {
    embedCode: ?string,
  };

  constructor(props) {
    super(props);
    this.state = {
      embedCode: null,
    };
  }

  componentWillMount() {
    this.loadEmbed();
  }

  componentDidUpdate(prevProps, prevState) {
    this.loadEmbed();
  }

  async loadEmbed() {
    const args = querystring.stringify({ url: this.props.url, format: 'json' });
    const oembedUrl = `https://soundcloud.com/oembed?${args}`;
    const result = await fetch(oembedUrl);
    const data = await result.json();
    this.setState({ embedCode: data.html });
  }

  render() {
    if (this.state.embedCode) {
      return <div dangerouslySetInnerHTML={{ __html: this.state.embedCode }} />; // eslint-disable-line react/no-danger
    } else {
      return <a href={this.props.url}>{this.props.url}</a>;
    }
  }
}

class FacebookPage extends React.Component {
  props: {
    username: string,
    amp: boolean,
  };

  render() {
    const pageUrl = `https://www.facebook.com/${this.props.username}/`;
    return this.props.amp ? (
      <span>
        <Helmet
          script={[
            {
              async: 'async',
              'custom-element': 'amp-facebook-like',
              src: 'https://cdn.ampproject.org/v0/amp-facebook-like-0.1.js',
            },
          ]}
        />
        <amp-facebook-like
          width="90"
          height="20"
          layout="fixed"
          data-href={pageUrl}
        />
      </span>
    ) : (
      <FBPage
        appId={this.props.username}
        href={pageUrl}
        height={300}
        smallHeader={false}
        adaptContainerWidth
        showFacepile
        tabs={['messages']}
      />
    );
  }
}

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

  addText(str) {
    if (!str) {
      return;
    }
    const remappers = {
      snapchat: username => (
        <a href={`http://www.snapchat.com/add/${username}`}>{username}</a>
      ),
      facebook: username => (
        <a href={`https://www.facebook.com/${username}`}>{username}</a>
      ),
      instagram: username => (
        <a href={`https://instagram.com/${username.replace('@', '')}`}>
          {username}
        </a>
      ),
      twitter: username => (
        <a href={`https://twitter.com/${username.replace('@', '')}`}>
          {username}
        </a>
      ),
    };
    let found = false;
    for (const keyword of Object.keys(remappers)) {
      const reString = `^(\\b${keyword}\\s*[:-]\\s*)(@?[\\w._-]+)`;
      const re = new RegExp(reString, 'i');
      const m = re.exec(str);
      if (m) {
        const fullMatchedString = m[1] + m[2];
        const startIndex = m.indexOf(fullMatchedString);
        const endIndex = startIndex + fullMatchedString.length;
        this.addText(str.slice(0, startIndex));
        this.elements.push(m[1]);
        this.elements.push(remappers[keyword](m[2]));
        this.addText(str.slice(endIndex, str.length));
        found = true;
        break;
      }
    }
    if (!found) {
      this.elements.push(str);
    }
  }
  splitNewlines(str, i) {
    const parts = str.split(/\n|\r/);

    parts.forEach((part, j) => {
      if (part) {
        this.addText(part);
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
    if (
      parsedUrl.host === 'www.youtube.com' &&
      parsedUrl.pathname === '/watch' &&
      parsedUrl.query &&
      parsedUrl.query.v
    ) {
      const videoId = parsedUrl.query.v;
      this.elements.push(
        this.options.amp ? (
          <span>
            <Helmet
              script={[
                {
                  async: 'async',
                  'custom-element': 'amp-youtube',
                  src: 'https://cdn.ampproject.org/v0/amp-youtube-0.1.js',
                },
              ]}
            />
            <amp-youtube
              data-videoid={videoId}
              layout="responsive"
              width="480"
              height="270"
            />
          </span>
        ) : (
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
        )
      );
    } else if (
      parsedUrl.host === 'www.youtube.com' &&
      parsedUrl.pathname === '/playlist' &&
      parsedUrl.query &&
      parsedUrl.query.list
    ) {
      const playlistId = parsedUrl.query.list;
      const embedUrl = `https://www.youtube.com/embed/videoseries?list=${playlistId}`;
      this.elements.push(
        this.options.amp ? (
          <span>
            <Helmet
              script={[
                {
                  async: 'async',
                  'custom-element': 'amp-iframe',
                  src: 'https://cdn.ampproject.org/v0/amp-iframe-0.1.js',
                },
              ]}
            />
            <amp-iframe
              src={embedUrl}
              layout="responsive"
              width="480"
              height="270"
              frameborder="0"
              allowfullscreen=""
              sandbox="allow-scripts allow-same-origin"
            />
          </span>
        ) : (
          <div key={i} className="video-container">
            <iframe
              id="ytplayer"
              type="text/html"
              width="640"
              height="360"
              src={embedUrl}
              frameBorder="0"
              allowFullScreen
            />
          </div>
        )
      );
    } else if (parsedUrl.host === 'www.soundcloud.com') {
      this.elements.push(<SoundCloud key={i} url={match.url} />);
    } else if (
      parsedUrl.host === 'www.facebook.com' ||
      (parsedUrl.pathname && !/^\/(?:events|groups|)/.test(parsedUrl.pathname))
    ) {
      const pathname = parsedUrl.pathname;
      let username = pathname.split('/')[1];
      if (username && username.includes('-')) {
        const splits = username.split('-');
        username = splits[splits.length - 1];
      }
      this.elements.push(
        <FacebookPage key={i} username={username} amp={this.options.amp} />
      );
    } else {
      this.elements.push(
        <a key={i} target={target} rel={rel} href={match.url}>
          {match.text}
        </a>
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

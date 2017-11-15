/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import * as React from 'react';

import type { Bracket, Match, Position } from './bracketModels';
import { BracketRenderer } from './bracketModels';

class MatchReact extends React.Component<
  {
    bracketRenderer: BracketRenderer,
    match: ?Match,
    position: Position,
  },
  {
    imageCounter: number,
  }
> {
  _intervalId: number;

  constructor(props) {
    super(props);
    (this: any).onMouseEnterHandler = this.onMouseEnterHandler.bind(this);
    (this: any).onMouseLeaveHandler = this.onMouseLeaveHandler.bind(this);
    this.state = {
      imageCounter: -1,
    };
  }

  onMouseEnterHandler() {
    this.setState({ imageCounter: 1 });
    this._intervalId = window.setInterval(() => {
      const nextCounter = (this.state.imageCounter + 1) % 3 + 1;
      this.setState({ imageCounter: nextCounter });
    }, 300);
  }

  onMouseLeaveHandler() {
    window.clearInterval(this._intervalId);
    this.setState({ imageCounter: -1 });
  }

  isHover() {
    return this.state.imageCounter > -1;
  }

  render() {
    const hoverStyle = {
      boxShadow: '0px 0px 15px #000',
    };
    const divStyle = {
      position: 'absolute',
      left: this.props.position.x,
      top: this.props.position.y,
      width: this.props.bracketRenderer.MatchWidth,
      height: this.props.bracketRenderer.MatchHeight,
      backgroundColor: 'transparent',
      borderColor: 'black',
      borderWidth: 1,
      borderStyle: 'solid',
      ...(this.isHover() ? hoverStyle : {}),
    };

    if (this.props.match) {
      let img = null;
      if (this.props.match.videoId) {
        const videoId = this.props.match.videoId;
        const imageName = this.isHover()
          ? this.state.imageCounter
          : 'sddefault';
        img = (
          <div
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
            }}
          >
            <img
              style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
              }}
              src={`https://i.ytimg.com/vi/${videoId}/${imageName}.jpg`}
              alt="video"
            />
            <div
              style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                backgroundColor: 'rgba(0, 0, 0, 0.3)',
              }}
            />
          </div>
        );
      }

      const contestants = [this.props.match.first, this.props.match.second];
      if (this.props.match && this.props.match.winner != null) {
        contestants[this.props.match.winner] = (
          <span style={{ fontWeight: 'bold', fontSize: '20' }}>
            {contestants[this.props.match.winner]}
          </span>
        );
      }

      let textOverlay = (
        <div
          style={{
            position: 'absolute',
            width: '100%',
            height: '100%',

            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <div
            style={{
              textAlign: 'center',
            }}
          >
            {contestants[0]}
            <br />
            vs<br />
            {contestants[1]}
          </div>
        </div>
      );

      if (this.props.match.videoId) {
        textOverlay = (
          <a
            style={{
              position: 'absolute',
              width: '100%',
              height: '100%',
              color: 'white',
            }}
            onMouseEnter={this.onMouseEnterHandler}
            onMouseLeave={this.onMouseLeaveHandler}
            href={`https://www.youtube.com/watch?v=${this.props.match.videoId}`}
          >
            {textOverlay}
          </a>
        );
      }

      return (
        <div style={divStyle}>
          {img}
          {textOverlay}
        </div>
      );
    } else {
      return <div style={divStyle} />;
    }
  }
}

class BracketLines extends React.Component<{
  bracketRenderer: BracketRenderer,
  left: number,
  right: number,
  top: number,
  bottom: number,
}> {
  render() {
    const box = {
      left: this.props.left,
      top: this.props.top,
      width:
        this.props.right -
        this.props.left -
        this.props.bracketRenderer.MatchGutterWidth / 2,
      height: this.props.bottom - this.props.top,
    };
    const line = {
      left: box.left + box.width,
      top: box.top + box.height / 2,
      width: this.props.bracketRenderer.MatchGutterWidth,
      height: 0,
    };
    return (
      <div>
        <div
          style={{
            position: 'absolute',
            border: '1px solid black',
            borderLeftWidth: 0,
            ...box,
          }}
        />
        <div
          style={{
            position: 'absolute',
            borderTop: '1px solid black',
            ...line,
          }}
        />
      </div>
    );
  }
}

class BracketReact extends React.Component<{
  bracket: Bracket,
}> {
  render() {
    const bracket = {
      matches: [
        { videoId: '5Xu_S_SpR0g', first: 'すずきゆうすけ', second: 'Hinoken' },
        {
          videoId: 'a-bZXFs-Z0U',
          first: 'ちっひー',
          second: 'すずきゆうすけ',
          winner: 1,
        },
        {
          videoId: 'zr6NOjIOB_8',
          first: 'Hinoken',
          second: 'YAMATO',
          winner: 0,
        },
        {
          videoId: 'Sl0-GQzOzvM',
          first: 'ちっひー',
          second: 'Hammer',
          winner: 0,
        },
        {
          videoId: '9P-UuCswG_4',
          first: 'すずきゆうすけ',
          second: 'ICHI',
          winner: 0,
        },
        {
          videoId: 'GX4FQ0ThAY4',
          first: 'ロケット',
          second: 'Hinoken',
          winner: 1,
        },
        {
          videoId: 'QpM1EjMLavc',
          first: 'YAMATO',
          second: 'Mao',
          winner: 0,
        },
        {
          videoId: 'e7jDEeksGy4',
          first: 'ちっひー',
          second: 'TAKUMA',
          winner: 0,
        },
        {
          videoId: 'FPtcEcMoeuc',
          first: 'Hammer',
          second: 'YASUHA',
          winner: 0,
        },
        {
          videoId: 'XzAhJYw8i2o',
          first: 'すずきゆうすけ',
          second: 'あおきま',
          winner: 0,
        },
        {
          videoId: 'RHHX8eNte40',
          first: 'Dunga D Doo',
          second: 'ICHI',
          winner: 1,
        },
        {
          videoId: '1n8qq4fsDck',
          first: 'KO-TA',
          second: 'ロケット',
          winner: 1,
        },
        {
          videoId: '7782ULGM8Qk',
          first: 'Hinoken',
          second: 'Masaaki',
          winner: 0,
        },
        {
          videoId: 'zg5XaK7-I8A',
          first: 'KAEDE',
          second: 'YAMATO',
          winner: 1,
        },
        { videoId: '78pGbGKRBjA', first: 'Mao', second: 'セル', winner: 0 },
      ],
    };
    const bracketRenderer = new BracketRenderer(bracket);
    const totalSize = bracketRenderer.getTotalSize();
    const matches = bracketRenderer
      .getMatchAndPositions()
      .map(({ match, position }, index) => (
        <MatchReact
          key={index}
          bracketRenderer={bracketRenderer}
          match={match}
          position={position}
        />
      ));
    const lines = [];

    // Start at 1, not 0. The final match (column 0) does not have an right-going bracket
    let matchIndex = 0;
    for (let i = 0; i < bracketRenderer.getTotalColumns(); i += 1) {
      if (i === 0) {
        matchIndex += 1;
        continue; // eslint-disable-line no-continue
      }
      for (let j = 0; j < bracketRenderer.getRowsInColumn(i); j += 2) {
        const topIndex = matchIndex + j;
        const upper = bracketRenderer.getPositionForMatchIndex(topIndex);
        const lower = bracketRenderer.getPositionForMatchIndex(topIndex + 1);
        const right =
          upper.x +
          bracketRenderer.MatchWidth +
          bracketRenderer.MatchGutterWidth;
        lines.push(
          <BracketLines
            key={topIndex}
            bracketRenderer={bracketRenderer}
            left={upper.x}
            right={right}
            top={upper.y + bracketRenderer.MatchHeight / 2}
            bottom={lower.y + bracketRenderer.MatchHeight / 2}
          />
        );
      }
      matchIndex += bracketRenderer.getRowsInColumn(i);
    }
    return (
      <div
        style={{
          position: 'relative',
          width: totalSize.width,
          height: totalSize.height,
        }}
      >
        {lines}
        {matches}
      </div>
    );
  }
}

export default BracketReact;

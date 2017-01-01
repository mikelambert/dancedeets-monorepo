/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import React from 'react';

import type {
  Bracket,
  Match,
  Position,
} from './bracketModels';
import {
  BracketRenderer,
} from './bracketModels';

class MatchReact extends React.Component {
  props: {
    bracketRenderer: BracketRenderer;
    match: Match;
    position: Position;
  }

  render() {
    const contestantStyle = {
      border: 1,
      backgroundColor: '#777',
      flex: 1,
    };

    const divStyle = {
      position: 'absolute',
      left: this.props.position.x,
      top: this.props.position.y,
      width: this.props.bracketRenderer.MatchWidth,
      height: this.props.bracketRenderer.MatchHeight,
      backgroundColor: 'white',
      display: 'flex',
      flexDirection: 'row',
    };
    let img = null;
    if (this.props.match.videoId) {
      img = (
        <a href={`https://www.youtube.com/watch?v=${this.props.match.videoId}`}>
          <img
            style={{
              width: 64,
              height: 48,
            }}
            src={`https://i.ytimg.com/vi/${this.props.match.videoId}/sddefault.jpg`}
            alt="video"
          />
        </a>
      );
    }

    return (<div style={divStyle}>
      {img}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div style={contestantStyle}>{this.props.match.first}</div>
        <div style={contestantStyle}>{this.props.match.second}</div>
      </div>
    </div>);
  }
}

class BracketLines extends React.Component {
  props: {
    bracketRenderer: BracketRenderer;
    left: number;
    right: number;
    top: number;
    bottom: number;
  };

  render() {
    const box = {
      left: this.props.left,
      top: this.props.top,
      width: this.props.right - this.props.left - this.props.bracketRenderer.MatchGutterWidth / 2,
      height: this.props.bottom - this.props.top,
    };
    const line = {
      left: box.left + box.width,
      top: box.top + box.height / 2,
      width: this.props.bracketRenderer.MatchGutterWidth,
      height: 0,
    };
    return (<div>
      <div style={{ position: 'absolute', border: '1px solid white', borderLeftWidth: 0, ...box }} />
      <div style={{ position: 'absolute', borderTop: '1px solid white', ...line }} />
    </div>);
  }
}

class BracketReact extends React.Component {
  props: {
    bracket: Bracket;
  }

  render() {
    const bracket = {
      matches: [
        { videoId: 'xGkCztkRmO8',
          first: '喜多パン粉愛好会',
          second: 'FUNBARE☆89\'s' },
        { videoId: 'pQAbUKur6-4',
          first: '最恐最悪反則crew',
          second: '喜多パン粉愛好会' },
        { videoId: '5swR67R8AaA',
          first: 'SST',
          second: 'FUNBARE☆89\'s' },
        { videoId: 'ukFPfbHOZMU',
          first: '最恐最悪反則crew',
          second: 'K uve doble' },
        { videoId: 'd8YGVRQ1DSQ',
          first: '隣の家の山田はアイアンマン',
          second: '喜多パン粉愛好会' },
        { videoId: 'Aw1lKvMfdm4', first: 'まこきん', second: 'SST' },
        { videoId: 'jOi1rfXc5U8',
          first: 'disclose',
          second: 'FUNBARE☆89\'s' },
        { videoId: 'iM-8154m3Fk', first: 'コダック', second: '最恐最悪反則crew' },
        { videoId: 'GlzVqUh1clc',
          first: 'ゆうきるか',
          second: 'K uve doble' },
        { videoId: 'wwn9cz80Y0o',
          first: 'Eden of The East',
          second: '隣の家の山田はアイアンマン' },
        { videoId: 'XHumrHZNU2g',
          first: '喜多パン粉愛好会',
          second: 'ちぇけらWALLY' },
        { videoId: 'M6_OJYGP4kI',
          first: 'あすてぃーとさらでぃー',
          second: 'まこきん' },
        { videoId: 'xbaqqwVEBR4', first: 'SST', second: 'パブリックエネミー' },
        { videoId: '1R-UW8IyXqY',
          first: 'シベリアン・ハスキー',
          second: 'disclose' },
        { videoId: 'Cb26mOaVVaM',
          first: 'Hectic',
          second: 'FUNBARE☆89\'s' },
      ],
    };
    const bracketRenderer = new BracketRenderer(bracket);
    const totalSize = bracketRenderer.getTotalSize();
    const matches = bracketRenderer.getMatchAndPositions().map(({ match, position }, index) =>
      <MatchReact key={index} bracketRenderer={bracketRenderer} match={match} position={position} />);
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
        const right = upper.x + bracketRenderer.MatchWidth + bracketRenderer.MatchGutterWidth;
        lines.push(<BracketLines
          key={topIndex}
          bracketRenderer={bracketRenderer}
          left={upper.x}
          right={right}
          top={upper.y + bracketRenderer.MatchHeight / 2}
          bottom={lower.y + bracketRenderer.MatchHeight / 2}
        />);
      }
      matchIndex += bracketRenderer.getRowsInColumn(i);
    }
    return (
      <div style={{ position: 'relative', width: totalSize.width, height: totalSize.height }}>
        {lines}
        {matches}
      </div>
    );
  }
}

export default BracketReact;

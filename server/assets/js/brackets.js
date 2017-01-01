import React from 'react';
import { sortNumber } from 'dancedeets-common/js/util/sort';

import {
  Bracket,
  BracketRenderer,
  Match,
  Position
} from './bracketsModels';

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
    };

    const divStyle = {
      position: 'absolute',
      left: this.props.position.x,
      top: this.props.position.y,
      width: this.props.bracketRenderer.MatchWidth,
      height: this.props.bracketRenderer.MatchHeight,
      backgroundColor: 'white',
    };
    return (<div style={divStyle}>
      <div style={contestantStyle}>{this.props.match.first.name} ({this.props.match.videoId})</div>
      <div style={contestantStyle}>{this.props.match.second.name}</div>
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
    const bracketRenderer = new BracketRenderer();
    bracketRenderer.matches = [
      { first: { name: 'Mike' }, second: { name: 'Mary' } },

      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },

      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },

      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },
      { first: { name: 'Mike' }, second: { name: 'Mary' } },

      { first: { name: 'Mike' }, second: { name: 'Mary' } },
    ];
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

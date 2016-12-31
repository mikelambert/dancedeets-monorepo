import React from 'react';
import { sortNumber } from 'dancedeets-common/js/util/sort';

type Contestant = {
  name: string;
};

type Match = {
  first: Contestant;
  second: Contestant;
  videoId?: string;
};

type Position = {
  x: number;
  y: number;
};

class Bracket {
  matches: Array<Match>;

  // 0 : finals
  // 1, 2: semi-finals
  // 3, 4, 5, 6: quarter-finals
  // etc

  constructor() {
    this.MatchWidth = 100;
    this.MatchHeight = 38;
    this.MatchGutterWidth = 30;
    this.MatchGutterHeight = 20;
  }

  getTotalColumns() {
    return Math.ceil(Math.log2(this.matches.length + 1));
  }

  getColumnForMatchIndex(matchCount) {
    return Math.floor(Math.log2(matchCount + 1));
  }

  getRowsInColumn(index) {
    return 2 ** index;
  }

  getTotalSize() {
    const columns = this.getTotalColumns();
    const width = this.MatchWidth * columns + this.MatchGutterWidth * (columns - 1);
    const rows = this.getRowsInColumn(columns - 1);
    const height = this.MatchHeight * rows + this.MatchGutterHeight * (rows - 1);
    return { width, height };
  }

  getPositionForMatchIndex(index) {
    const totalSize = this.getTotalSize();
    const totalColumns = this.getTotalColumns();
    const column = this.getColumnForMatchIndex(index);
    const x = totalSize.width - (this.MatchWidth * (column + 1) + this.MatchGutterWidth * column);
    const matchHeightWithMargin = totalSize.height / this.getRowsInColumn(column);
    const totalMatchesInEarlierColumns = this.getRowsInColumn(column) - 1;
    const rowIndex = index - totalMatchesInEarlierColumns;
    const y = matchHeightWithMargin * rowIndex + matchHeightWithMargin / 2 - this.MatchHeight / 2;
    // This results in a small bit of gutter at the top and bottom of each column,
    // due to how it spaces everything out. This looks fine for most columns,
    // but feels a bit off on the first column. Too bad...it's all margin anyway.
    return { x, y };
  }

  getMatchAndPositions() {
    const results = this.matches.map((match, index) => ({
      match,
      sortKey: -this.getColumnForMatchIndex(index) * this.matches.length + index,
      position: this.getPositionForMatchIndex(index),
    }));
    // sort by sortKey, and then remove it from the results we return
    return sortNumber(results, x => x.sortKey).map(({ match, position }) => ({ match, position }));
  }
}

class MatchReact extends React.Component {
  props: {
    bracket: Bracket;
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
      width: this.props.bracket.MatchWidth,
      height: this.props.bracket.MatchHeight,
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
    bracket: Bracket;
    left: number;
    right: number;
    top: number;
    bottom: number;
  };

  render() {
    const box = {
      left: this.props.left,
      top: this.props.top,
      width: this.props.right - this.props.left - this.props.bracket.MatchGutterWidth / 2,
      height: this.props.bottom - this.props.top,
    };
    const line = {
      left: box.left + box.width,
      top: box.top + box.height / 2,
      width: this.props.bracket.MatchGutterWidth,
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
    const bracket = new Bracket();
    bracket.matches = [
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
    const totalSize = bracket.getTotalSize();
    const matches = bracket.getMatchAndPositions().map(({ match, position }, index) =>
      <MatchReact key={index} bracket={bracket} match={match} position={position} />);
    const lines = [];

    // Start at 1, not 0. The final match (column 0) does not have an right-going bracket
    let matchIndex = 0;
    for (let i = 0; i < bracket.getTotalColumns(); i += 1) {
      if (i === 0) {
        matchIndex += 1;
        continue; // eslint-disable-line no-continue
      }
      for (let j = 0; j < bracket.getRowsInColumn(i); j += 2) {
        const topIndex = matchIndex + j;
        const upper = bracket.getPositionForMatchIndex(topIndex);
        const lower = bracket.getPositionForMatchIndex(topIndex + 1);
        const right = upper.x + bracket.MatchWidth + bracket.MatchGutterWidth;
        lines.push(<BracketLines
          key={topIndex}
          bracket={bracket}
          left={upper.x}
          right={right}
          top={upper.y + bracket.MatchHeight / 2}
          bottom={lower.y + bracket.MatchHeight / 2}
        />);
      }
      matchIndex += bracket.getRowsInColumn(i);
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

import React from 'react';

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
    this.MatchHeight = 40;
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
    const width = (this.MatchWidth * columns) + (this.MatchGutterWidth * (columns - 1));
    const rows = this.getRowsInColumn(columns - 1);
    const height = (this.MatchHeight * rows) + (this.MatchGutterHeight * (rows - 1));
    return { width, height };
  }

  getPositionFromIndex(index) {
    const totalSize = this.getTotalSize();
    const totalColumns = this.getTotalColumns();
    const column = this.getColumnForMatchIndex(index);
    console.log({ index, column, temp: Math.log2(index + 1), temp2: Math.ceil(Math.log2(index + 1)) });
    const x = (totalSize.width - (this.MatchWidth * (column + 1))) - (this.MatchGutterWidth * (column - 1));
    const matchHeightWithMargin = totalSize.height / this.getRowsInColumn(column);
    const totalMatchesInEarlierColumns = this.getRowsInColumn(column) - 1;
    const rowIndex = index - totalMatchesInEarlierColumns;
    const y = (matchHeightWithMargin * rowIndex) + (matchHeightWithMargin / 2);
    console.log({ index, column, rowIndex, x, y });
    return { x, y };
  }

  getMatchAndPositions() {
    return this.matches.map((match, index) => ({
      match,
      position: this.getPositionFromIndex(index),
    }));
  }
}

class MatchReact extends React.Component {
  props: {
    match: Match;
    position: Position;
  }

  render() {
    const contestantStyle = {
      border: 1,
      backgroundColor: '#777',
    };

    return (<div style={{ position: 'absolute', left: this.props.position.x, top: this.props.position.y }}>
      <div style={contestantStyle}>{this.props.match.first.name} ({this.props.match.videoId})</div>
      <div style={contestantStyle}>{this.props.match.second.name}</div>
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
      <MatchReact key={index} match={match} position={position} />);
    return (
      <div style={{ position: 'relative', width: totalSize.width, height: totalSize.height }}>
        {matches}
      </div>
    );
  }
}

export default BracketReact;

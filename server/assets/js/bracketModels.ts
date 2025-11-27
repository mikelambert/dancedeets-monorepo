/**
 * Copyright 2016 DanceDeets.
 */

import { sortNumber } from 'dancedeets-common/js/util/sort';

export type Contestant = string;

export interface Match {
  first: Contestant;
  second: Contestant;
  winner?: 0 | 1 | null;
  videoId?: string;
}

export interface Position {
  x: number;
  y: number;
}

export interface Bracket {
  matches: Array<Match | null>;
}

export class BracketRenderer {
  matches: Array<Match | null>;

  // 0 : finals
  // 1, 2: semi-finals
  // 3, 4, 5, 6: quarter-finals
  // etc

  MatchWidth: number;
  MatchHeight: number;
  MatchGutterWidth: number;
  MatchGutterHeight: number;

  constructor(bracket: Bracket) {
    this.matches = bracket.matches;
    this.MatchWidth = 240;
    this.MatchHeight = 180;
    this.MatchGutterWidth = 30;
    this.MatchGutterHeight = 20;
  }

  getMatch(column: number, row: number): Match | null {
    const matchIndex = 2 ** column - 1 + row;
    return this.matches[matchIndex];
  }

  getTotalColumns(): number {
    return Math.ceil(Math.log2(this.matches.length + 1));
  }

  getColumnForMatchIndex(matchCount: number): number {
    return Math.floor(Math.log2(matchCount + 1));
  }

  getRowsInColumn(index: number): number {
    return 2 ** index;
  }

  getTotalSize(): { width: number; height: number } {
    const columns = this.getTotalColumns();
    const width =
      this.MatchWidth * columns + this.MatchGutterWidth * (columns - 1);
    const rows = this.getRowsInColumn(columns - 1);
    const height =
      this.MatchHeight * rows + this.MatchGutterHeight * (rows - 1);
    return { width, height };
  }

  getPositionForMatchIndex(index: number): Position {
    const totalSize = this.getTotalSize();
    const column = this.getColumnForMatchIndex(index);
    const x =
      totalSize.width -
      (this.MatchWidth * (column + 1) + this.MatchGutterWidth * column);
    const matchHeightWithMargin =
      totalSize.height / this.getRowsInColumn(column);
    const totalMatchesInEarlierColumns = this.getRowsInColumn(column) - 1;
    const rowIndex = index - totalMatchesInEarlierColumns;
    const y =
      matchHeightWithMargin * rowIndex +
      matchHeightWithMargin / 2 -
      this.MatchHeight / 2;
    // This results in a small bit of gutter at the top and bottom of each column,
    // due to how it spaces everything out. This looks fine for most columns,
    // but feels a bit off on the first column. Too bad...it's all margin anyway.
    return { x, y };
  }

  getMatchAndPositions(): Array<{ match: Match | null; position: Position }> {
    const results = this.matches.map((match, index) => ({
      match,
      sortKey:
        -this.getColumnForMatchIndex(index) * this.matches.length + index,
      position: this.getPositionForMatchIndex(index),
    }));
    // sort by sortKey, and then remove it from the results we return
    return sortNumber(results, x => x.sortKey).map(({ match, position }) => ({
      match,
      position,
    }));
  }
}

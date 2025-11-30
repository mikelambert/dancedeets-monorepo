/**
 * Unit tests for util/sort.ts
 */

import { sortString, sortNumber } from '../../util/sort';

describe('sortString', () => {
  it('should sort objects by string property', () => {
    const items = [
      { name: 'Charlie' },
      { name: 'Alice' },
      { name: 'Bob' },
    ];
    const result = sortString(items, item => item.name);
    expect(result.map(i => i.name)).toEqual(['Alice', 'Bob', 'Charlie']);
  });

  it('should sort strings directly', () => {
    const items = ['Charlie', 'Alice', 'Bob'];
    const result = sortString(items, x => x);
    expect(result).toEqual(['Alice', 'Bob', 'Charlie']);
  });

  it('should handle empty array', () => {
    const result = sortString([], () => '');
    expect(result).toEqual([]);
  });

  it('should handle single element', () => {
    const result = sortString(['single'], x => x);
    expect(result).toEqual(['single']);
  });

  it('should handle duplicates by preserving them', () => {
    const items = [
      { id: 1, category: 'B' },
      { id: 2, category: 'A' },
      { id: 3, category: 'B' },
    ];
    const result = sortString(items, item => item.category);
    expect(result.map(i => i.id)).toEqual([2, 1, 3]);
  });

  it('should sort numbers as strings (lexicographic order)', () => {
    const items = ['10', '2', '1', '20'];
    const result = sortString(items, x => x);
    // Lexicographic: "1" < "10" < "2" < "20"
    expect(result).toEqual(['1', '10', '2', '20']);
  });

  it('should handle computed string values', () => {
    const items = [
      { first: 'John', last: 'Doe' },
      { first: 'Jane', last: 'Smith' },
      { first: 'Bob', last: 'Adams' },
    ];
    const result = sortString(items, item => item.last);
    expect(result.map(i => i.last)).toEqual(['Adams', 'Doe', 'Smith']);
  });

  it('should convert numbers to strings via compute function', () => {
    const items = [{ score: 100 }, { score: 50 }, { score: 75 }];
    const result = sortString(items, item => item.score);
    // String sorting: "100" < "50" < "75"
    expect(result.map(i => i.score)).toEqual([100, 50, 75]);
  });

  it('should handle mixed case strings', () => {
    const items = ['banana', 'Apple', 'cherry', 'Apricot'];
    const result = sortString(items, x => x);
    // Capital letters come before lowercase in ASCII
    expect(result).toEqual(['Apple', 'Apricot', 'banana', 'cherry']);
  });
});

describe('sortNumber', () => {
  it('should sort objects by numeric property', () => {
    const items = [
      { score: 50 },
      { score: 100 },
      { score: 25 },
    ];
    const result = sortNumber(items, item => item.score);
    expect(result.map(i => i.score)).toEqual([25, 50, 100]);
  });

  it('should sort numbers directly', () => {
    const items = [10, 5, 20, 1];
    const result = sortNumber(items, x => x);
    expect(result).toEqual([1, 5, 10, 20]);
  });

  it('should handle empty array', () => {
    const result = sortNumber([], () => 0);
    expect(result).toEqual([]);
  });

  it('should handle single element', () => {
    const result = sortNumber([42], x => x);
    expect(result).toEqual([42]);
  });

  it('should handle negative numbers', () => {
    const items = [5, -10, 0, -5, 10];
    const result = sortNumber(items, x => x);
    expect(result).toEqual([-10, -5, 0, 5, 10]);
  });

  it('should handle duplicates by preserving them', () => {
    const items = [
      { id: 'a', value: 10 },
      { id: 'b', value: 5 },
      { id: 'c', value: 10 },
    ];
    const result = sortNumber(items, item => item.value);
    expect(result.map(i => i.id)).toEqual(['b', 'a', 'c']);
  });

  it('should sort in ascending order by default', () => {
    const items = [100, 1, 50, 25, 75];
    const result = sortNumber(items, x => x);
    expect(result).toEqual([1, 25, 50, 75, 100]);
  });

  it('should support descending order via negation', () => {
    const items = [{ value: 100 }, { value: 1 }, { value: 50 }];
    const result = sortNumber(items, item => -item.value);
    expect(result.map(i => i.value)).toEqual([100, 50, 1]);
  });

  it('should handle floating point numbers', () => {
    const items = [1.5, 2.5, 1.0, 2.0];
    const result = sortNumber(items, x => x);
    expect(result).toEqual([1.0, 1.5, 2.0, 2.5]);
  });

  it('should handle computed values', () => {
    const items = [
      { width: 10, height: 5 },  // area: 50
      { width: 3, height: 3 },   // area: 9
      { width: 5, height: 4 },   // area: 20
    ];
    const result = sortNumber(items, item => item.width * item.height);
    expect(result.map(i => i.width * i.height)).toEqual([9, 20, 50]);
  });

  it('should handle zeros', () => {
    const items = [5, 0, -5, 0, 10];
    const result = sortNumber(items, x => x);
    expect(result).toEqual([-5, 0, 0, 5, 10]);
  });
});

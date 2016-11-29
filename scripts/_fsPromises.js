/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

'use strict';
import * as fs from 'fs';
import * as path from 'path';

export function walk(dir: string) {
  var results = [];
  return new Promise((resolve, reject) => {
    fs.readdir(dir, function(err, list) {
      if (err) {
        return reject(err);
      }
      var pending = list.length;
      if (!pending) {
        return resolve(results);
      }
      list.forEach(function(file) {
        file = path.resolve(dir, file);
        fs.stat(file, function(err2, stat) {
          if (stat && stat.isDirectory()) {
            walk(file).then(function(res) {
              results = results.concat(res);
              if (!--pending) {
                resolve(results);
              }
            });
          } else {
            results.push(file);
            if (!--pending) {
              resolve(results);
            }
          }
        });
      });
    });
  });
}

export function writeFile(filename: string, contents: string) {
  return new Promise((resolve, reject) => {
    fs.writeFile(filename, contents, (err) => {
      if (err) {
        reject(err);
      } else {
        resolve(path.resolve(filename));
      }
    });
  });
}

export function readFile(filename: string) {
  return new Promise((resolve, reject) => {
    fs.readFile(filename, (err, data) => {
      if (err) {
        reject(err);
      } else {
        resolve(data);
      }
    });
  });
}

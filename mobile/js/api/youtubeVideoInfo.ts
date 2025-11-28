import * as urllib from 'url';
import * as querystring from 'querystring';
// @ts-ignore - ytdl-core types may not be available
import * as util from 'ytdl-core/lib/util';
// @ts-ignore - ytdl-core types may not be available
import * as FORMATS from 'ytdl-core/lib/formats';

const VIDEO_URL = 'https://www.youtube.com/watch?v=';
const EMBED_URL = 'https://www.youtube.com/embed/';
const VIDEO_EURL = 'https://youtube.googleapis.com/v/';
const THUMBNAIL_URL = 'https://i.ytimg.com/vi/';
const INFO_HOST = 'www.youtube.com';
const INFO_PATH = '/get_video_info';
const KEYS_TO_SPLIT = ['keywords', 'fmt_list', 'fexp', 'watermark'];

interface RequestOptions {
  requestOptions?: any;
  lang?: string;
  debug?: boolean;
}

interface VideoInfo {
  formats: any[];
  author?: any;
  published?: any;
  description?: string;
  related_videos?: any[];
  video_url?: string;
  iurlsd?: string;
  iurlmq?: string;
  iurlhq?: string;
  iurlmaxres?: string;
  [key: string]: any;
}

interface YtConfig {
  args: any;
  sts?: string;
}

async function request(
  url: string,
  options: any,
  callback: (error: Error | null, result?: any, body?: string) => void
): Promise<void> {
  console.log(url);
  let result = null;
  try {
    result = await fetch(url);
  } catch (e: any) {
    callback(e);
    return;
  }
  callback(null, result, await result.text());
}

/**
 * Gets info from a video.
 */
function getInfo(link: string, options?: RequestOptions): Promise<VideoInfo>;
function getInfo(
  link: string,
  options: RequestOptions,
  callback: (err: Error | null, info?: VideoInfo) => void
): void;
function getInfo(
  link: string,
  callback: (err: Error | null, info?: VideoInfo) => void
): void;
function getInfo(
  link: string,
  optionsOrCallback?: RequestOptions | ((err: Error | null, info?: VideoInfo) => void),
  maybeCallback?: (err: Error | null, info?: VideoInfo) => void
): Promise<VideoInfo> | void {
  let options: RequestOptions;
  let callback: ((err: Error | null, info?: VideoInfo) => void) | undefined;

  if (typeof optionsOrCallback === 'function') {
    callback = optionsOrCallback;
    options = {};
  } else if (!optionsOrCallback) {
    options = {};
  } else {
    options = optionsOrCallback;
    callback = maybeCallback;
  }

  if (!callback) {
    return new Promise<VideoInfo>((resolve, reject) => {
      getInfo(link, options, (err: Error | null, info?: VideoInfo) => {
        if (err) return reject(err);
        resolve(info!);
      });
    });
  }

  const id = util.getVideoID(link);
  if (id instanceof Error) return callback(id);

  // Try getting config from the video page first.
  const url = VIDEO_URL + id + '&hl=' + (options.lang || 'en');

  request(url, options.requestOptions, (err: Error | null, res?: any, body?: string) => {
    if (err) return callback!(err);

    // Check if there are any errors with this video page.
    const unavailableMsg = util.between(
      body,
      '<div id="player-unavailable"',
      '>'
    );
    if (
      unavailableMsg &&
      !/\bhid\b/.test(util.between(unavailableMsg, 'class="', '"'))
    ) {
      // Ignore error about age restriction.
      if (body!.indexOf('<div id="watch7-player-age-gate-content"') < 0) {
        return callback!(
          new Error(
            util
              .between(
                body,
                '<h1 id="unavailable-message" class="message">',
                '</h1>'
              )
              .trim()
          )
        );
      }
    }

    // Parse out some additional informations since we already load that page.
    const additional: Partial<VideoInfo> = {
      // Get informations about the author/uploader.
      author: util.getAuthor(body),

      // Get the day the vid was published.
      published: util.getPublished(body),

      // Get description from #eow-description.
      description: util.getVideoDescription(body),

      // Get related videos.
      related_videos: util.getRelatedVideos(body),

      // Give the canonical link to the video.
      video_url: url,

      // Thumbnails.
      iurlsd: THUMBNAIL_URL + id + '/sddefault.jpg',
      iurlmq: THUMBNAIL_URL + id + '/mqdefault.jpg',
      iurlhq: THUMBNAIL_URL + id + '/hqdefault.jpg',
      iurlmaxres: THUMBNAIL_URL + id + '/maxresdefault.jpg',
    };

    let jsonStr = util.between(body, 'ytplayer.config = ', '</script>');
    let config: string;
    if (jsonStr) {
      config = jsonStr.slice(0, jsonStr.lastIndexOf(';ytplayer.load'));
      gotConfig2(id, options, additional, config, false, callback!);
    } else {
      // If the video page doesn't work, maybe because it has mature content.
      // and requires an account logged into view, try the embed page.
      const embedUrl = EMBED_URL + id + '?hl=' + (options.lang || 'en');

      request(embedUrl, options.requestOptions, (err: Error | null, res?: any, body?: string) => {
        if (err) return callback!(err);
        config = util.between(body, "t.setConfig({'PLAYER_CONFIG': ", "},'");
        gotConfig2(id, options, additional, config, true, callback!);
      });
    }
  });
}

function gotConfig2(
  id: string,
  options: RequestOptions,
  additional: Partial<VideoInfo>,
  config: string,
  appendConfig: boolean,
  callback: (err: Error | null, info?: VideoInfo) => void
): void {
  if (!config) {
    return callback(new Error('Could not find player config'));
  }
  let parsedConfig: YtConfig;
  try {
    parsedConfig = JSON.parse(config + (appendConfig ? '}' : ''));
  } catch (err: any) {
    return callback(new Error('Error parsing config: ' + err.message));
  }
  const info: VideoInfo = { ...parsedConfig.args, ...additional };
  info.formats = util.parseFormats(info);
  callback(null, info);
}

/**
 * @param {Object} id
 * @param {Object} options
 * @param {Object} additional
 * @param {Object} config
 * @param {Boolean} appendConfig
 * @param {Function(Error, Object)} callback
 */
function gotConfig(
  id: string,
  options: RequestOptions,
  additional: Partial<VideoInfo>,
  config: string,
  appendConfig: boolean,
  callback: (err: Error | null, info?: VideoInfo) => void
): void {
  if (!config) {
    return callback(new Error('Could not find player config'));
  }
  let parsedConfig: YtConfig;
  try {
    parsedConfig = JSON.parse(config + (appendConfig ? '}' : ''));
  } catch (err: any) {
    return callback(new Error('Error parsing config: ' + err.message));
  }
  const url = urllib.format({
    protocol: 'https',
    host: INFO_HOST,
    pathname: INFO_PATH,
    query: {
      video_id: id,
      eurl: VIDEO_EURL + id,
      ps: 'default',
      gl: 'US',
      hl: options.lang || 'en',
      sts: parsedConfig.sts,
    },
  });
  request(url, options.requestOptions, (err: Error | null, res?: any, body?: string) => {
    if (err) return callback(err);
    let info: any = querystring.parse(body!);
    if (info.status === 'fail') {
      info = parsedConfig.args;
    } else if (info.requires_purchase === '1') {
      return callback(new Error(info.ypc_video_rental_bar_text));
    }

    // Split some keys by commas.
    KEYS_TO_SPLIT.forEach((key: string) => {
      if (!info[key]) return;
      info[key] = info[key].split(',').filter((v: string) => v !== '');
    });

    info.fmt_list = info.fmt_list
      ? info.fmt_list.map((format: string) => format.split('/'))
      : [];

    info.formats = util.parseFormats(info);

    // Add additional properties to info.
    info = util.objectAssign(info, additional, false);
    gotFormats();

    function gotFormats() {
      if (options.debug) {
        info.formats.forEach((format: any) => {
          const itag = format.itag;
          if (!FORMATS[itag]) {
            console.warn('No format metadata for itag ' + itag + ' found');
          }
        });
      }
      info.formats.forEach(util.addFormatMeta);
      info.formats.sort(util.sortFormats);
      callback(null, info);
    }
  });
}

/**
 * @param {String} url
 * @param {Array.<String>} tokens
 */
function decipherURL(url: string, tokens: string[]): string {
  return url.replace(/\/s\/([a-fA-F0-9\.]+)/, (_, s) => {
    // Note: sig is not imported, this function may not work correctly
    // return '/signature/' + sig.decipher(tokens, s);
    return '/signature/' + s;
  });
}

/**
 * Merges formats from DASH or M3U8 with formats from video info page.
 *
 * @param {Object} info
 * @param {Object} formatsMap
 */
function mergeFormats(info: VideoInfo, formatsMap: Record<string, any>): void {
  info.formats.forEach((f: any) => {
    const cf = formatsMap[f.itag];
    if (cf) {
      for (const key in f) {
        cf[key] = f[key];
      }
    } else {
      formatsMap[f.itag] = f;
    }
  });
  info.formats = [];
  for (const itag in formatsMap) {
    info.formats.push(formatsMap[itag]);
  }
}

/**
 * Gets additional formats.
 *
 * @param {String} url
 * @param {Object} options
 * @param {Function(!Error, Array.<Object>)} callback
 */
function getM3U8(
  url: string,
  options: RequestOptions,
  callback: (err: Error | null, formats?: Record<string, any>) => void
): void {
  url = urllib.resolve(VIDEO_URL, url);
  request(url, options.requestOptions, (err: Error | null, res?: any, body?: string) => {
    if (err) return callback(err);

    const formats: Record<string, any> = {};
    body!
      .split('\n')
      .filter((line: string) => /https?:\/\//.test(line))
      .forEach((line: string) => {
        const match = line.match(/\/itag\/(\d+)\//);
        if (match) {
          const itag = match[1];
          formats[itag] = { itag: itag, url: line };
        }
      });
    callback(null, formats);
  });
}

export default getInfo;

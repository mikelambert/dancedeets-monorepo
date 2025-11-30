/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { useIntl } from 'react-intl';
import YouTube from 'react-youtube';
import Helmet from 'react-helmet';
import ExecutionEnvironment from 'exenv';
import { intlWeb } from 'dancedeets-common/js/intl';
import { getTutorials } from 'dancedeets-common/js/tutorials/playlistConfig';
import { Playlist, Video } from 'dancedeets-common/js/tutorials/models';
import { formatDuration } from 'dancedeets-common/js/tutorials/format';
import { Link, ShareLinks, wantsWindowSizes } from './ui';
import type { WindowProps } from './ui';
import { generateMetaTags } from './meta';

const backgroundPlaylistHeaderColor = 'white';
const backgroundSectionHeaderColor = '#656595';
const backgroundVideoColor = 'white';
const backgroundVideoColorActive = '#E0E0F5';

// Calculate header height dynamically to account for navbar + promo messages
const getHeaderHeight = (): number => {
  if (typeof document === 'undefined') return 50;
  const navbar = document.querySelector('.navbar');
  const promoMessages = document.querySelector('.alert.alert-info');
  let height = 0;
  if (navbar) height += (navbar as HTMLElement).offsetHeight;
  if (promoMessages) height += (promoMessages as HTMLElement).offsetHeight;
  return height || 50;
};

interface DurationProps {
  duration: number;
  style?: React.CSSProperties;
}

function Duration({ duration, style }: DurationProps): React.ReactElement {
  const intl = useIntl();
  const formattedDuration = formatDuration(
    intl.formatMessage,
    duration
  );
  return (
    <div
      style={{
        fontSize: '80%',
        ...style,
      }}
    >
      {formattedDuration}
    </div>
  );
}

interface TutorialViewProps {
  tutorial: Playlist;
  videoIndex: number | null;
  window?: WindowProps | null;
}

function TutorialViewInner({ tutorial, videoIndex: initialVideoIndex, window: windowProp }: TutorialViewProps): React.ReactElement {
  const intl = useIntl();
  const [video, setVideo] = React.useState<Video>(tutorial.getVideo(initialVideoIndex || 0));
  const youtubeRef = React.useRef<YouTube | null>(null);
  const prevVideoRef = React.useRef<Video>(video);

  React.useEffect(() => {
    if (initialVideoIndex !== null) {
      setVideo(tutorial.getVideo(initialVideoIndex || 0));
    }
  }, [initialVideoIndex, tutorial]);

  React.useEffect(() => {
    if (prevVideoRef.current !== video) {
      const currentVideoIndex = tutorial.getVideoIndex(video);
      const oldHash = window.location.hash || '#0';
      const newHash = `#${currentVideoIndex}`;
      if (oldHash !== newHash) {
        window.location.hash = newHash;
      }

      window.mixpanel?.track('Tutorial Video Selected', {
        tutorialName: tutorial.title,
        tutorialStyle: tutorial.style,
        tutorialVideoIndex: currentVideoIndex,
      });
      prevVideoRef.current = video;
    }
  }, [video, tutorial]);

  function onVideoClick(clickedVideo: Video): void {
    setVideo(clickedVideo);
  }

  function onVideoEnd(): void {
    const currentVideoIndex = tutorial.getVideoIndex(video) + 1;
    if (currentVideoIndex < tutorial.getVideoCount()) {
      const nextVideo = tutorial.getVideo(currentVideoIndex);
      setVideo(nextVideo);
    }
  }

  function renderVideoLine(lineVideo: Video): React.ReactElement {
    const activeRow = video.youtubeId === lineVideo.youtubeId;
    const backgroundColor = activeRow
      ? backgroundVideoColorActive
      : backgroundVideoColor;

    return (
      <Link
        onClick={() => onVideoClick(lineVideo)}
        style={{
          backgroundColor,
          display: 'flex',
          alignItems: 'center',
          padding: 7,
          borderBottomWidth: 0.5,
          borderBottomStyle: 'solid',
          borderBottomColor: backgroundSectionHeaderColor,
        }}
      >
        <div>
          <i
            className="fa fa-play-circle"
            aria-hidden="true"
            style={{ fontSize: '200%' }}
          />
        </div>
        <div style={{ marginLeft: 10 }}>
          <div style={{ fontWeight: 'bold' }}>{lineVideo.title}</div>
          <Duration
            duration={lineVideo.getDurationSeconds()}
            style={{ color: '#777' }}
          />
        </div>
      </Link>
    );
  }

  function renderSectionHeader(section: { title: string; getDurationSeconds: () => number }): React.ReactElement {
    return (
      <div
        style={{
          color: 'white',
          padding: 7,
          backgroundColor: backgroundSectionHeaderColor,
        }}
      >
        <div>{section.title}</div>
        <Duration duration={section.getDurationSeconds()} />
      </div>
    );
  }

  function renderWholeSection(section: { title: string; videos: Video[]; getDurationSeconds: () => number }): React.ReactElement {
    return (
      <div>
        {renderSectionHeader(section)}
        {section.videos.map((sectionVideo) => (
          <div key={sectionVideo.youtubeId}>{renderVideoLine(sectionVideo)}</div>
        ))}
      </div>
    );
  }

  function renderHeader(): React.ReactElement {
    const subtitle = tutorial.subtitle ? <div>{tutorial.subtitle}</div> : null;
    const duration = formatDuration(
      intl.formatMessage,
      tutorial.getDurationSeconds()
    );
    const subline = `${tutorial.author} - ${duration}`;
    return (
      <div
        style={{ padding: 7, backgroundColor: backgroundPlaylistHeaderColor }}
      >
        <h3 style={{ marginTop: 0 }}>
          {tutorial.title} - <a href="/tutorials">See All Tutorials</a>
        </h3>
        {subtitle}
        <div>{subline}</div>
        <ShareLinks url={tutorial.getUrl()} />
      </div>
    );
  }

  function renderPlayer(): React.ReactElement {
    return (
      <div
        className="video-player-container"
        style={{
          flex: 2,
          width: '100%',
          height: '100%',
          backgroundColor: '#000',
        }}
      >
        <YouTube
          ref={x => {
            youtubeRef.current = x;
          }}
          opts={{
            width: '100%',
            height: '100%',
            playerVars: {
              autoplay: 1,
            },
          }}
          videoId={video.youtubeId}
          onEnd={onVideoEnd}
        />
      </div>
    );
  }

  const height = windowProp
    ? windowProp.height - getHeaderHeight()
    : '100vh';
  return (
    <div
      className="media-width-row-or-column"
      style={{
        display: 'flex',
        height,
      }}
    >
      {renderPlayer()}
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          minHeight: 0,
          minWidth: 0,
        }}
      >
        {renderHeader()}
        {tutorial.sections.map((section) => (
          <div key={section.title}>{renderWholeSection(section)}</div>
        ))}
      </div>
    </div>
  );
}
const TutorialView = wantsWindowSizes(TutorialViewInner);

interface StyleConfig {
  tutorials: Playlist[];
}

function findTutorialById(config: StyleConfig[], id: string): Playlist | null {
  let foundTutorial: Playlist | null = null;
  config.forEach(style => {
    style.tutorials.forEach(tutorialItem => {
      if (tutorialItem.getId() === id) {
        foundTutorial = tutorialItem;
      }
    });
  });
  return foundTutorial;
}

interface HtmlHeadProps {
  tutorial: Playlist | null;
  videoIndex: number | null;
}

function HtmlHead({ tutorial, videoIndex }: HtmlHeadProps): React.ReactElement {
  let title = 'Unknown tutorial';
  let metaTags: Array<{ property?: string; name?: string; content: string }> = [];
  if (tutorial) {
    title = tutorial.title;
    if (videoIndex != null) {
      const video = tutorial.getVideo(videoIndex);
      title += `: ${video.title}`;
    }
    title += ' | DanceDeets Tutorial';

    metaTags = generateMetaTags(title, tutorial.getUrl(), tutorial.thumbnail);
  }

  return <Helmet title={title} meta={metaTags} />;
}

interface TutorialPageProps {
  style: string;
  tutorial: string;
  hashLocation: string;
  currentLocale: string;
}

function TutorialPage({ style, tutorial: tutorialId, hashLocation, currentLocale }: TutorialPageProps): React.ReactElement {
  const intl = useIntl();
  const trackedRef = React.useRef(false);

  function trackTutorial(tutorial: Playlist): void {
    if (!ExecutionEnvironment.canUseDOM) {
      return;
    }
    if (!trackedRef.current) {
      trackedRef.current = true;
      window.mixpanel?.track('Tutorial Selected', {
        tutorialName: tutorial.title,
        tutorialStyle: tutorial.style,
      });
    }
  }

  const config = getTutorials(intl.locale);
  const tutorial = findTutorialById(config, tutorialId);

  let result: React.ReactElement;
  const videoIndex = hashLocation
    ? parseInt(hashLocation, 10)
    : null;
  if (tutorial) {
    trackTutorial(tutorial);
    result = (
      <TutorialView
        tutorial={tutorial}
        videoIndex={videoIndex}
      />
    );
  } else {
    result = <div>Unknown tutorial!</div>;
  }
  return (
    <div>
      <HtmlHead tutorial={tutorial} videoIndex={videoIndex} />
      {result}
    </div>
  );
}

export const HelmetRewind = Helmet.rewind;
export default intlWeb(TutorialPage);

// Window extensions
declare global {
  interface Window {
    sentMixpanelPing?: boolean;
  }
}

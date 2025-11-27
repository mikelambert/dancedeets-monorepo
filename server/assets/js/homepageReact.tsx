/**
 * Copyright 2016 DanceDeets.
 */

import * as React from 'react';
import { cdnBaseUrl } from 'dancedeets-common/js/util/url';
// We have another import that is only in homepageReactExec.js (since we want it clientside)

interface MobileAppUrls {
  ios: string;
  android: string;
}

interface FullPagePromoProps {
  mobilePlatform: 'android' | 'ios' | null;
  mobileAppUrls: MobileAppUrls;
  ipLocation: string;
}

class FullPagePromo extends React.Component<FullPagePromoProps> {
  render(): React.ReactNode {
    const mobilePromos = [
      this.props.mobilePlatform !== 'android' ? (
        <a href={this.props.mobileAppUrls.ios} key="ios">
          <img
            src={`${cdnBaseUrl}/img/app_store_download.png`}
            className="store-button"
            alt="Download from App Store"
          />
        </a>
      ) : null,
      this.props.mobilePlatform !== 'ios' ? (
        <a href={this.props.mobileAppUrls.android} key="android">
          <img
            src={`${cdnBaseUrl}/img/play_store_download.png`}
            className="store-button"
            alt="Download from Google Play Store"
          />
        </a>
      ) : null,
    ];

    return (
      <div className="flush-top fullscreen-static-image bg-color-darker">
        <div className="fullscreen-darken-image">
          <div className="container text-center vertical-center">
            <div className="dancedeets-tagline color-light margin-bottom-30">
              Street Dance Events. Worldwide.
            </div>
            <div className="col-md-6 col-md-offset-3 margin-bottom-30">
              <form action="/" className="margin-bottom-20">
                <div className="input-group">
                  <input
                    id="location"
                    name="location"
                    type="text"
                    className="form-control"
                    placeholder="Enter a city or country"
                    defaultValue={this.props.ipLocation}
                  />
                  <span className="input-group-btn">
                    <button id="location_submit" className="btn btn-primary">
                      <i className="fa fa-search" /> Find Your Dance
                    </button>
                  </span>
                </div>
              </form>
              <div className="color-light margin-bottom-20">
                or find events on the go
              </div>
              {mobilePromos}
            </div>
            <div className="dancedeets-tagline-small color-light">
              Get up offa that thing, and dance 'til you feel better – James
              Brown
            </div>
          </div>
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              right: 0,
              color: 'white',
            }}
          >
            Photo Credits:{' '}
            <a href="https://www.facebook.com/mario.lobo.90">Mario Lobo</a> and{' '}
            <a href="http://dangitslim.com/">Slim</a>.
          </div>
        </div>
      </div>
    );
  }
}

interface UseCasesProps {
  ipLocation: string;
}

class UseCases extends React.Component<UseCasesProps> {
  render(): React.ReactNode {
    return (
      <div>
        <h2>Lookup Event</h2>
        <form>
          <input type="text" name="event_name" />
          <button>Lookup Event</button>
        </form>
        <hr />
        <h2>Upcoming Events</h2>
        Near you in {this.props.ipLocation}: Today | Tomorrow | Saturday |
        Sunday | See All
        <hr />
        <h2>Planning a Trip?</h2>
        [where] and [when] <button>Plan My Trip</button>
        <hr />
        <h2>Host an Event</h2>
        <button>Start Planning!</button>
      </div>
    );
  }
}

class FeaturePromos extends React.Component {
  render(): React.ReactNode {
    return (
      <div className="content-md">
        <div className="container">
          <div className="row text-center">
            <div className="col-md-4 md-margin-bottom-50">
              <img
                alt=""
                srcSet={`${cdnBaseUrl}/img/deets-activity-dancing.png 1x, ${cdnBaseUrl}/img/deets-activity-dancing.svg 2x`}
                src={`${cdnBaseUrl}/img/deets-activity-dancing.png`}
                className="deets-activity-image margin-bottom-20"
              />
              <h2 className="title-v3-md margin-bottom-10">
                Learning to dance?
              </h2>
              <p>
                Want to go beyond the classroom?<br />
                Find all the battles, shows,<br />
                parties, workshops, and more!
              </p>
            </div>
            <div className="col-md-4 md-margin-bottom-50">
              <img
                alt=""
                srcSet={`${cdnBaseUrl}/img/deets-activity-traveling.png 1x, ${cdnBaseUrl}/img/deets-activity-traveling.svg 2x`}
                src={`${cdnBaseUrl}/img/deets-activity-traveling.png`}
                className="deets-activity-image margin-bottom-20"
              />
              <h2 className="title-v3-md margin-bottom-10">Going on a trip?</h2>
              <p>
                Want to meet other dancers?<br />
                Quickly ﬁnd the dance scene anywhere,<br />
                and start connecting in real-life!
              </p>
            </div>
            <div className="col-md-4">
              <img
                alt=""
                srcSet={`${cdnBaseUrl}/img/deets-activity-flyering.png 1x, ${cdnBaseUrl}/img/deets-activity-flyering.svg 2x`}
                src={`${cdnBaseUrl}/img/deets-activity-flyering.png`}
                className="deets-activity-image margin-bottom-20"
              />
              <h2 className="title-v3-md margin-bottom-10">
                Promoting events?
              </h2>
              <p>
                With over 20,000 dancers monthly,<br />
                and 80,000 dance events since 2010,<br />
                it's the best source for street dance events.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

interface DisplayItem {
  text: string;
  image: string;
  url: string;
}

interface SeeMore {
  text: string;
  url: string;
}

interface MultipleItemsProps {
  headerText: string;
  items: DisplayItem[];
  seeMore?: SeeMore;
}

class MultipleItems extends React.Component<MultipleItemsProps> {
  render(): React.ReactNode {
    return (
      <div className="container margin-bottom-60">
        <div className="headline">
          <h2>{this.props.headerText}</h2>
        </div>

        <div className="row">
          {this.props.items.map(item => (
            <div key={item.image} className="col-md-4">
              <div className="panel panel-default">
                <div className="panel-body">
                  <a href={item.url} className="zoom">
                    <div className="text-overlay">{item.text}</div>
                    <img src={`${cdnBaseUrl}${item.image}`} alt="" />
                  </a>
                </div>
              </div>
            </div>
          ))}
          {this.props.seeMore ? (
            <div className="row">
              <div
                className="col-sm-3 col-sm-offset-9"
                style={{ textAlign: 'right' }}
              >
                <a href={this.props.seeMore.url}>{this.props.seeMore.text}</a>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    );
  }
}

interface FullPageProps {
  mobilePlatform: 'android' | 'ios' | null;
  mobileAppUrls: MobileAppUrls;
  ipLocation: string;
}

export default class FullPage extends React.Component<FullPageProps> {
  render(): React.ReactNode {
    const dummy = <UseCases key="use-cases" ipLocation={this.props.ipLocation} />; // eslint-disable-line no-unused-vars, @typescript-eslint/no-unused-vars
    return [
      <FullPagePromo
        key="promo"
        mobilePlatform={this.props.mobilePlatform}
        mobileAppUrls={this.props.mobileAppUrls}
        ipLocation={this.props.ipLocation}
      />,
      <FeaturePromos key="feature-promos" />,
      <MultipleItems
        key="cities"
        headerText="Popular Cities"
        items={[
          {
            text: 'New York',
            url: '/?location=NYC',
            image: '/img/location-new-york.jpg',
          },
          {
            text: 'Los Angeles',
            url: '/?location=Los+Angeles',
            image: '/img/location-los-angeles.jpg',
          },
          {
            text: 'Paris',
            url: '/?location=Paris',
            image: '/img/location-paris.jpg',
          },
        ]}
        seeMore={{ text: 'See more cities.', url: '/rankings' }}
      />,
      <MultipleItems
        key="styles"
        headerText="Popular Styles"
        items={[
          {
            text: 'Breaking',
            url: '/style/breaking',
            image: '/img/style-bboy.jpg',
          },
          {
            text: 'Popping',
            url: '/style/popping',
            image: '/img/style-popping.jpg',
          },
          {
            text: 'Hiphop & Street-Jazz',
            url: '/style/hip-hop',
            image: '/img/style-hiphop.jpg',
          },
        ]}
        seeMore={{ text: 'See more cities.', url: '/rankings' }}
      />,
    ];
  }
}

/**
 * Copyright 2016 DanceDeets.
 */

import jQuery from 'jquery';
import * as React from 'react';
import PropTypes from 'prop-types';
import Scroll from 'react-scroll';
import { format as dateFormat } from 'date-fns';
import { intlWeb } from 'dancedeets-common/js/intl';
import {
  MultiSelectList,
  generateUniformState,
  caseInsensitiveSort,
  getSelected,
} from './MultiSelectList';
import type { MultiSelectState } from './MultiSelectList';

interface SerializedStudioClass {
  url: string;
  name: string;
  location: string;
  startTime: string;
  categories: Array<string>;
  key: string;
  sponsor?: string;
}

interface StudioClassType {
  url: string;
  name: string;
  location: string;
  startTime: Date;
  categories: Array<string>;
  key: string;
  sponsor?: string;
}

interface StudioImageProps {
  studioName: string;
}

class StudioImage extends React.Component<StudioImageProps> {
  static contextTypes = {
    imagePath: PropTypes.string,
  };

  context!: { imagePath: string };

  render(): React.ReactElement {
    const imageSrc = `${this.context.imagePath +
      this.props.studioName.toLowerCase()}.png`;
    return (
      <img
        alt={this.props.studioName}
        src={imageSrc}
        role="presentation"
        width="16"
        height="16"
      />
    );
  }
}

function getDayId(dayName: string): string {
  return dayName;
}

interface DayLinkProps {
  dayName: string;
}

class DayLink extends React.Component<DayLinkProps> {
  constructor(props: DayLinkProps) {
    super(props);
    this.onClick = this.onClick.bind(this);
  }

  onClick(): void {
    Scroll.scroller.scrollTo(this.props.dayName, {
      smooth: true,
      delay: 100,
      duration: 500,
      offset: -(jQuery('#navbar').outerHeight() as number + 20),
    });
  }

  render(): React.ReactElement {
    return (
      <a href={`#${getDayId(this.props.dayName)}`} onClick={this.onClick}>
        {this.props.dayName}
      </a>
    );
  }
}

// TODO: i18n?
const dayOfWeekNames = [
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
];

class DayNavMenu extends React.Component {
  render(): React.ReactElement {
    const weeks: React.ReactNode[] = [];
    for (let i = 0; i < 7; i += 1) {
      if (i > 0) {
        weeks.push(<span key={`|-${i}`}> | </span>);
      }
      const dayName = dayOfWeekNames[i];
      weeks.push(<DayLink key={dayName} dayName={dayName} />);
    }
    return (
      <span className="navmenu-height headline-underline">
        Jump to: {weeks}
      </span>
    );
  }
}

type ValidKey = 'styles' | 'studios' | 'teacher';

interface SearchBarProps {
  initialStudios: Array<string>;
  initialStyles: Array<string>;
  studios: MultiSelectState;
  styles: MultiSelectState;
  teacher: string;
  onChange: (key: ValidKey, newState: unknown) => void;
}

class SearchBar extends React.Component<SearchBarProps> {
  _styles: MultiSelectList | null = null;
  _studios: MultiSelectList | null = null;
  _teacher: HTMLInputElement | null = null;

  render(): React.ReactElement {
    return (
      <form className="form-inline">
        <div>
          Styles:{' '}
          <MultiSelectList
            list={this.props.initialStyles}
            selected={this.props.styles}
            ref={x => {
              this._styles = x;
            }}
            onChange={state => this.props.onChange('styles', state)}
          />
        </div>
        <div>
          Studios:{' '}
          <MultiSelectList
            list={this.props.initialStudios}
            selected={this.props.studios}
            ref={x => {
              this._studios = x;
            }}
            onChange={state => this.props.onChange('studios', state)}
            itemRenderer={item => (
              <span>
                <StudioImage key="image" studioName={item} />
                {item}
              </span>
            )}
          />
        </div>
        <div>
          Teacher:{' '}
          <input
            className="form-control"
            type="text"
            value={this.props.teacher}
            ref={x => {
              this._teacher = x;
            }}
            onChange={() =>
              this._teacher
                ? this.props.onChange('teacher', this._teacher.value)
                : null}
          />
        </div>
      </form>
    );
  }
}

interface ClassSummaryProps {
  styles: Array<string>;
  studios: Array<string>;
  teacher: string;
}

class ClassSummary extends React.Component<ClassSummaryProps> {
  render(): React.ReactElement {
    let classes = this.props.styles.join(', ');
    if (!classes) {
      classes = 'All';
    }
    let studios = this.props.studios.join(', ');
    if (studios) {
      studios = `at ${studios}`;
    }
    let query = this.props.teacher;
    if (query) {
      query = `with "${query}"`;
    }

    return (
      <div>
        {classes} classes {studios} {query}
      </div>
    );
  }
}

interface StudioClassProps {
  studio_class: StudioClassType;
}

class StudioClass extends React.Component<StudioClassProps> {
  render(): React.ReactElement {
    return (
      <div style={{ marginLeft: 40, marginBottom: 2 }}>
        <a href={this.props.studio_class.url}>
          <StudioImage studioName={this.props.studio_class.location} />
        </a>
        {this.props.studio_class.location}: {this.props.studio_class.name}
      </div>
    );
  }
}

interface DayHeaderProps {
  date: Date;
  useAnchor: boolean;
}

class DayHeader extends React.Component<DayHeaderProps> {
  render(): React.ReactElement {
    let contents: React.ReactElement = <h4>{dateFormat(this.props.date, 'ddd MMM D')}</h4>;
    if (this.props.useAnchor) {
      contents = (
        <div>
          <Scroll.Element
            name={getDayId(dateFormat(this.props.date, 'dddd'))}
          />
          {contents}
        </div>
      );
    }
    return contents;
  }
}

interface TimeHeaderProps {
  datetime: Date;
}

class TimeHeader extends React.Component<TimeHeaderProps> {
  render(): React.ReactElement {
    return <b>{dateFormat(this.props.datetime, 'h:mma')}</b>;
  }
}

interface ClassTitleProps {
  filteredClasses: Array<StudioClassType>;
}

class ClassTitle extends React.Component<ClassTitleProps> {
  render(): React.ReactElement {
    const { filteredClasses } = this.props;
    return (
      <div>
        <b>Showing {filteredClasses.length} classes:</b>
      </div>
    );
  }
}

interface SponsoredSummaryProps {
  classes: Array<StudioClassType>;
}

class SponsoredSummary extends React.Component<SponsoredSummaryProps> {
  render(): React.ReactElement {
    const sponsoredStudios: Record<string, Record<string, boolean>> = {};
    this.props.classes.forEach(studioClass => {
      const { sponsor } = studioClass;
      if (!sponsor) {
        return;
      }
      if (!(sponsor in sponsoredStudios)) {
        sponsoredStudios[sponsor] = {};
      }
      const studio = studioClass.location;
      sponsoredStudios[sponsor][studio] = true;
    });
    const sponsorHtml: React.ReactElement[] = [];
    if ('MINDBODY' in sponsoredStudios) {
      const studioList = Object.keys(sponsoredStudios.MINDBODY);
      sponsorHtml.push(
        <div key="MINDBODY" style={{ margin: '1em 0em', fontStyle: 'italic' }}>
          Studios Powered by{' '}
          <a href="http://www.mindbodyonline.com">MINDBODY</a>
          : {studioList.join(', ')}
        </div>
      );
    }
    return <div>{sponsorHtml}</div>;
  }
}

interface StudioClassesProps {
  filteredClasses: Array<StudioClassType>;
}

class StudioClasses extends React.Component<StudioClassesProps> {
  render(): React.ReactElement {
    const rows: React.ReactElement[] = [];
    let lastStudioClass: StudioClassType | null = null;
    const goodClasses = this.props.filteredClasses;
    const aNamedDays: Record<string, boolean> = {};
    goodClasses.forEach((studioClass: StudioClassType) => {
      // Section header rendering
      if (
        lastStudioClass === null ||
        dateFormat(studioClass.startTime, 'YYYY-MM-DD') !==
          dateFormat(lastStudioClass.startTime, 'YYYY-MM-DD')
      ) {
        const day = dateFormat(studioClass.startTime, 'dddd');
        rows.push(
          <DayHeader
            date={studioClass.startTime}
            key={dateFormat(studioClass.startTime, 'YYYY-MM-DD')}
            useAnchor={!aNamedDays[day]}
          />
        );
        aNamedDays[day] = true;
      }
      if (
        lastStudioClass === null ||
        dateFormat(studioClass.startTime, 'HH:mm') !==
          dateFormat(lastStudioClass.startTime, 'HH:mm')
      ) {
        rows.push(
          <TimeHeader
            datetime={studioClass.startTime}
            key={dateFormat(studioClass.startTime, 'YYYY-MM-DDTHH:mm')}
          />
        );
      }
      // Class rendering
      rows.push(
        <StudioClass studio_class={studioClass} key={studioClass.key} />
      );
      lastStudioClass = studioClass;
    });
    return <div>{rows}</div>;
  }
}

function toggleSearchBar(): void {
  jQuery('#navbar-collapsable').slideToggle('fast');
  const icon = jQuery('#navbar-collapse-button-icon');
  if (icon.hasClass('fa-caret-square-o-up')) {
    icon.removeClass('fa-caret-square-o-up');
    icon.addClass('fa-caret-square-o-down');
    jQuery('#navbar-collapsed-summary').show();
  } else {
    icon.removeClass('fa-caret-square-o-down');
    icon.addClass('fa-caret-square-o-up');
    jQuery('#navbar-collapsed-summary').hide();
  }
}

function parseISO(str: string): Date {
  const s = str.split(/\D/);
  return new Date(
    Number(s[0]),
    Number(s[1]) - 1,
    Number(s[2]),
    Number(s[3]),
    Number(s[4]),
    Number(s[5]),
    0
  );
}

interface AppProps {
  imagePath: string;
  classes: Array<SerializedStudioClass>;
  location: string;
  currentLocale: string;
}

interface AppState {
  styles: MultiSelectState;
  studios: MultiSelectState;
  teacher: string;
  initialClasses: Array<StudioClassType>;
  initialStudios: Array<string>;
  initialStyles: Array<string>;
}

class App extends React.Component<AppProps, AppState> {
  static childContextTypes = {
    imagePath: PropTypes.string,
  };

  constructor(props: AppProps) {
    super(props);
    const studiosSet: Record<string, boolean> = {};
    const stylesSet: Record<string, boolean> = {};
    this.props.classes.forEach(studioClass => {
      studiosSet[studioClass.location] = true;
      studioClass.categories.forEach(category => {
        if (category !== 'All-Styles') {
          stylesSet[category] = true;
        }
      });
    });
    const newClasses = this.props.classes.map(studioClass => {
      const { startTime, ...rest } = studioClass;
      return { startTime: parseISO(startTime), ...rest };
    });

    const studios = Object.keys(studiosSet).sort(caseInsensitiveSort);
    const styles = Object.keys(stylesSet).sort(caseInsensitiveSort);

    this.state = {
      studios: generateUniformState(studios, true),
      styles: generateUniformState(styles, true),
      teacher: '',
      initialClasses: newClasses,
      initialStudios: studios,
      initialStyles: styles,
    };

    this.onChange = this.onChange.bind(this);
  }

  getChildContext(): { imagePath: string } {
    return { imagePath: this.props.imagePath };
  }

  componentDidMount(): void {
    const allowedTime = 500; // maximum time allowed to travel that distance
    let startX: number;
    let startY: number;
    let startTime: number;
    let skipScroll = false;

    jQuery('#navbar').on({
      touchstart(jqueryEvent: JQuery.TouchStartEvent) {
        const e = jqueryEvent.originalEvent as TouchEvent;
        if (!e.changedTouches) {
          return;
        }
        const touchobj = e.changedTouches[0];
        skipScroll = true;
        startX = touchobj.pageX;
        startY = touchobj.pageY;
        startTime = new Date().getTime(); // record time when finger first makes contact with surface
        console.log((touchobj.target as HTMLElement).localName);
      },
      touchmove(jqueryEvent: JQuery.TouchMoveEvent) {
        if (skipScroll) {
          jqueryEvent.preventDefault();
        }
      },
      touchend(jqueryEvent: JQuery.TouchEndEvent) {
        skipScroll = false;
        const e = jqueryEvent.originalEvent as TouchEvent;
        const touchobj = e.changedTouches[0];
        const elapsedTime = new Date().getTime() - startTime; // get time elapsed
        const validSwipe =
          elapsedTime <= allowedTime &&
          Math.abs(touchobj.pageY - startY) > 50 &&
          Math.abs(touchobj.pageX - startX) <= 100;
        if (validSwipe) {
          if (
            jQuery('#navbar-collapsable').is(':visible') &&
            touchobj.pageY < startY
          ) {
            toggleSearchBar();
            jqueryEvent.preventDefault();
          }
          if (
            !jQuery('#navbar-collapsable').is(':visible') &&
            touchobj.pageY > startY
          ) {
            toggleSearchBar();
            jqueryEvent.preventDefault();
          }
        }
      },
    });
  }

  componentDidUpdate(): void {
    // Now scroll back so the navbar is directly at the top of the screen
    // and all of the results start fresh, beneath it
    const normalAffixedTop = jQuery('#navbar-container').offset()?.top || 0;
    if (jQuery(document).scrollTop()! > normalAffixedTop) {
      window.scroll(0, normalAffixedTop);
    }
  }

  onChange(key: ValidKey, state: unknown): void {
    this.setState({ [key]: state } as Pick<AppState, ValidKey>);
  }

  filteredClasses(): Array<StudioClassType> {
    const goodClasses: Array<StudioClassType> = [];
    const { state } = this;
    this.state.initialClasses.forEach(studioClass => {
      // Class filtering logic
      if (state.teacher) {
        if (
          studioClass.name
            .toLowerCase()
            .indexOf(state.teacher.toLowerCase()) === -1
        ) {
          return;
        }
      }
      if (
        getSelected(state.studios).filter(
          studio => studio === studioClass.location
        ).length === 0
      ) {
        return;
      }
      if (
        getSelected(state.styles).filter(searchStyle => {
          const classHasStyle = studioClass.categories.filter(
            classStyle => searchStyle === classStyle
          );
          return classHasStyle.length > 0;
        }).length === 0
      ) {
        return;
      }
      goodClasses.push(studioClass);
    });
    return goodClasses;
  }

  render(): React.ReactElement {
    const filteredClasses = this.filteredClasses();
    return (
      <div>
        <div
          id="navbar-container"
          style={{
            marginBottom: '1em',
          }}
        >
          <div
            className="headline"
            id="navbar"
            style={{
              zIndex: 50,
            }}
          >
            <table>
              <tbody>
                <tr>
                  <td style={{ width: '100%' }}>
                    <div id="navbar-collapsable" className="navmenu-height">
                      <b>{this.props.location} Street Dance Classes</b>
                      <SearchBar
                        initialStudios={this.state.initialStudios}
                        initialStyles={this.state.initialStyles}
                        styles={this.state.styles}
                        studios={this.state.studios}
                        teacher={this.state.teacher}
                        onChange={this.onChange}
                      />
                    </div>
                    <div id="navbar-collapsed-summary">
                      <ClassSummary
                        styles={getSelected(this.state.styles)}
                        studios={getSelected(this.state.studios)}
                        teacher={this.state.teacher}
                      />
                    </div>
                    <DayNavMenu />
                  </td>
                  <td style={{ verticalAlign: 'bottom' }}>
                    <span // eslint-disable-line jsx-a11y/click-events-have-key-events
                      onClick={toggleSearchBar}
                      role="button"
                      tabIndex={-1}
                    >
                      <i
                        id="navbar-collapse-button-icon"
                        className="fa fa-caret-square-o-up fa-lg"
                      />
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div>
          <ClassTitle filteredClasses={filteredClasses} />
          <StudioClasses filteredClasses={filteredClasses} />
          <SponsoredSummary classes={this.state.initialClasses} />
        </div>
      </div>
    );
  }
}

export default intlWeb(App);

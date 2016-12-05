/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
/* global $ */


import React from 'react';
import dateFormat from 'date-fns/format';

type DateTime = any;
type StudioClassType = any;

class StudioImage extends React.Component {
  props: {
    studioName: string;
  }

  render() {
    const imageSrc = `${this.context.imagePath + this.props.studioName.toLowerCase()}.png`;
    return (
      <img src={imageSrc} role="presentation" width="16" height="16" />
    );
  }
}
StudioImage.contextTypes = {
  imagePath: React.PropTypes.string,
};

class SelectButton extends React.Component {
  props: {
    onChange: () => void;
    value: boolean;
    thumbnail?: boolean;
    item: any;
  }

  _button: React.Element<*>;

  toggleState(e) {
    this.manualToggleState();
    this.props.onChange();
    e.preventDefault();
  }

  manualToggleState() {
    const button = $(this._button);
    button.toggleClass('active');
    button.blur();
  }

  isActive() {
    return $(this._button).hasClass('active');
  }

  render() {
    let extraClass = '';
    if (this.props.value) {
      extraClass = 'active';
    }
    const contents = [];
    if (this.props.thumbnail) {
      contents.push(<StudioImage studioName={this.props.item} />);
    }
    contents.push(this.props.item);

    return (
      <button
        type="button"
        className={`btn btn-default btn-sm ${extraClass}`}
        ref={(x) => { this._button = x; }}
        onClick={this.toggleState}
      >
        {contents}
      </button>
    );
  }
}

class MultiSelectList<T> extends React.Component {
  props: {
    onChange: () => void;
    list: Array<T>;
    value: T;
    thumbnails?: boolean;
  }

  _itemRefs: { [id: string]: SelectButton };

  constructor(props) {
    super(props);
    this._itemRefs = {};
  }

  getValues() {
    const values = [];
    this.props.list.forEach((item, i) => {
      if (this._itemRefs[`item${i}`].isActive()) {
        values.push(item);
      }
    });
    return values;
  }

  setAll() {
    this.props.list.forEach((item, i) => {
      if (this._itemRefs[`item${i}`].isActive()) {
        this._itemRefs[`item${i}`].manualToggleState();
      }
    });
    // Ensure we leave it active
    if (!this._itemRefs['item-all'].isActive()) {
      this._itemRefs['item-all'].manualToggleState();
    }
    this.props.onChange();
  }

  unsetAll() {
    if (this._itemRefs['item-all'].isActive()) {
      this._itemRefs['item-all'].manualToggleState();
    }

    let anySet = false;
    this.props.list.forEach((item, i) => {
      if (this._itemRefs[`item${i}`].isActive()) {
        anySet = true;
      }
    });
    if (!anySet) {
      this._itemRefs['item-all'].manualToggleState();
    }

    this.props.onChange();
  }

  render() {
    const options = [];
    const emptyList = (this.props.value.length === 0);
    options.push(
      <SelectButton key="All" item="All" ref={(x) => { this._itemRefs['item-all'] = x; }} value={emptyList} onChange={this.setAll} />
    );
    const thumbnails = this.props.thumbnails;
    const value = this.props.value;
    const unsetAll = this.unsetAll;
    this.props.list.forEach((item, i) => {
      let subItems = [item];
      let realItem = item;
      if (item.constructor === Array) {
        subItems = item[1];
        realItem = item[0];
      }

      let selected = true;
      subItems.forEach((subItem) => {
        selected = selected && (value.indexOf(subItem) !== -1);
      });

      options.push(
        <SelectButton key={realItem} item={realItem} ref={`item${i}`} value={selected} onChange={unsetAll} thumbnail={thumbnails} />
      );
    });
    return (
      <div className="btn-group" role="group">
        {options}
      </div>
    );
  }
}

function getDayId(dayName) {
  return dayName;
}

class DayLink extends React.Component {
  props: {
    dayName: string;
  }

  onClick() {
    const id = getDayId(this.props.dayName);
    if ($(`#${id}`).length === 0) {
      return;
    }
    const scrollOffset = $('#navbar').outerHeight();
    const nudgeOffset = 5;
    $('html, body').animate({ scrollTop: $(`#${id}`).offset().top - scrollOffset - nudgeOffset }, 300);
    // return false; // React does not require that onClick handlers return false
  }

  render() {
    return (
      <a href={`#${getDayId(this.props.dayName)}`} onClick={this.onClick}>{this.props.dayName}</a>
    );
  }
}

// TODO: i18n?
const dayOfWeekNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

class DayNavMenu extends React.Component {
  render() {
    const weeks = [];
    for (let i = 0; i < 7; i += 1) {
      if (i > 0) {
        weeks.push(<span key={`|-${i}`}> | </span>);
      }
      const dayName = dayOfWeekNames[i];
      weeks.push(
        <DayLink
          key={dayName}
          dayName={dayName}
        />
      );
    }
    return (
      <span className="navmenu-height headline-underline">Jump to:
      {' '}
        {weeks}
      </span>
    );
  }
}

class SearchBar extends React.Component {
  props: {
    initialStudios: Array<any>;
    initialStyles: Array<any>;
    studios: Array<any>;
    styles: Array<any>;
    teacher: string;
    onUserInput: (styles: Array<any>, studios: Array<any>, teacher: string) => void;
  }
  _styles: React.Element<MultiSelectList>;
  _studios: React.Element<MultiSelectList>;
  _teacher: React.Element<*>;

  onChange() {
    this.props.onUserInput(
      this._styles.getValues(),
      this._studios.getValues(),
      this._teacher.value
    );
  }

  render() {
    return (
      <form>
        <div>
          Styles:{' '}
          <MultiSelectList
            list={this.props.initialStyles}
            value={this.props.styles}
            ref={(x) => { this._styles = x; }}
            onChange={this.onChange}
          />
        </div>
        <div>
          Studios:{' '}
          <MultiSelectList
            list={this.props.initialStudios}
            value={this.props.studios}
            ref={(x) => { this._studios = x; }}
            onChange={this.onChange}
            thumbnails
          />
        </div>
        <div>
          Teacher:{' '}
          <input
            type="text"
            value={this.props.teacher}
            ref={(x) => { this._teacher = x; }}
            onChange={this.onChange}
          />
        </div>
      </form>
    );
  }
}

class ClassSummary extends React.Component {
  props: {
    styles: Array<string>;
    studios: Array<string>;
    teacher: string;
  }

  render() {
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

class StudioClass extends React.Component {
  props: {
    studio_class: StudioClassType;
  }

  render() {
    return (
      <div>
        <a href={this.props.studio_class.url}>
          <StudioImage studioName={this.props.studio_class.location} />
        </a>
        {this.props.studio_class.location}: {this.props.studio_class.name}
      </div>
    );
  }
}

class DayHeader extends React.Component {
  props: {
    date: DateTime;
    useAnchor: boolean;
  }

  render() {
    let contents = (
      <h4>{dateFormat(this.props.date, 'ddd MMM D')}</h4>
    );
    if (this.props.useAnchor) {
      contents = (
        <div id={getDayId(dateFormat(this.props.date, 'dddd'))}>
          {contents}
        </div>
      );
    }
    return contents;
  }
}

class TimeHeader extends React.Component {
  props: {
    datetime: DateTime;
  }

  render() {
    return (
      <b>{dateFormat(this.props.datetime, 'h:mma')}</b>
    );
  }
}

class ClassTitle extends React.Component {
  props: {
    filteredClasses: Array<StudioClassType>;
  }
  render() {
    const filteredClasses = this.props.filteredClasses;
    return (
      <div><b>Showing {filteredClasses.length} classes:</b></div>
    );
  }
}

class SponsoredSummary extends React.Component {
  props: {
    classes: Array<StudioClassType>;
  }

  render() {
    const sponsoredStudios = {};
    this.props.classes.forEach((studioClass) => {
      const sponsor = studioClass.sponsor;
      if (!(sponsor in sponsoredStudios)) {
        sponsoredStudios[sponsor] = {};
      }
      const studio = studioClass.location;
      sponsoredStudios[sponsor][studio] = true;
    });
    const sponsorHtml = [];
    if ('MINDBODY' in sponsoredStudios) {
      const studioList = Object.keys(sponsoredStudios.MINDBODY);
      sponsorHtml.push(
        <div key="MINDBODY" style={{ margin: '1em 0em', fontStyle: 'italic' }}>
          Studios Powered by <a href="http://www.mindbodyonline.com">MINDBODY</a>:{' '}
          {studioList.join(', ')}
        </div>
      );
    }
    return (
      <div>{sponsorHtml}</div>
    );
  }
}

class StudioClasses extends React.Component {
  props: {
    filteredClasses: Array<StudioClassType>;
  }

  render() {
    const rows = [];
    let lastStudioClass = null;
    const goodClasses = this.props.filteredClasses;
    const aNamedDays = {};
    goodClasses.forEach((studioClass) => {
      // Section header rendering
      if (lastStudioClass === null || dateFormat(studioClass.startTime, 'YYYY-MM-DD') !== dateFormat(lastStudioClass.startTime, 'YYYY-MM-DD')) {
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
      if (lastStudioClass === null || dateFormat(studioClass.startTime, 'HH:mm') !== dateFormat(lastStudioClass.startTime, 'HH:mm')) {
        rows.push(<TimeHeader datetime={studioClass.startTime} key={dateFormat(studioClass.startTime, 'YYYY-MM-DDTHH:mm')} />);
      }
      // Class rendering
      rows.push(<StudioClass studio_class={studioClass} key={studioClass.key} />);
      lastStudioClass = studioClass;
    });
    return <div>{rows}</div>;
  }
}

function toggleSearchBar() {
  $('#navbar-collapsable').slideToggle('fast');
  const icon = $('#navbar-collapse-button-icon');
  if (icon.hasClass('fa-caret-square-o-up')) {
    icon.removeClass('fa-caret-square-o-up');
    icon.addClass('fa-caret-square-o-down');
    $('#navbar-collapsed-summary').show();
  } else {
    icon.removeClass('fa-caret-square-o-down');
    icon.addClass('fa-caret-square-o-up');
    $('#navbar-collapsed-summary').hide();
  }
}

function parseISO(str) {
  const s = str.split(/\D/);
  return new Date(Number(s[0]), Number(s[1]) - 1, Number(s[2]), Number(s[3]), Number(s[4]), Number(s[5]), 0);
}

type AppProps = {
  imagePath: string,
  classes: Array<StudioClassType>;
  location: string;
};

export default class App extends React.Component {
  props: AppProps;

  state: {
    styles: Array<string>;
    studios: Array<string>;
    teacher: string;
    initialClasses: Array<StudioClassType>;
    initialStudios: Array<string>;
    initialStyles: Array<string>;
  }

  constructor(props: AppProps) {
    super(props);
    const studiosSet = {};
    const stylesSet = {};
    this.props.classes.forEach((studioClass) => {
      studiosSet[studioClass.location] = true;
      studioClass.categories.forEach((category) => {
        if (category !== 'All-Styles') {
          stylesSet[category] = true;
        }
      });
    });
    const newClasses = this.props.classes.map((studioClass) => {
      const { startTime, ...rest } = studioClass;
      return { startTime: parseISO(startTime), ...rest };
    });
    function caseInsensitiveSort(a, b) {
      return a.toLowerCase().localeCompare(b.toLowerCase());
    }

    this.state = {
      styles: [],
      studios: [],
      teacher: '',
      initialClasses: newClasses,
      initialStudios: Object.keys(studiosSet).sort(caseInsensitiveSort),
      initialStyles: Object.keys(stylesSet).sort(caseInsensitiveSort),
    };

    (this: any).handleUserInput = this.handleUserInput.bind(this);
  }

  getChildContext() {
    return { imagePath: this.props.imagePath };
  }

  componentDidMount() {
    const allowedTime = 500; // maximum time allowed to travel that distance
    let startX;
    let startY;
    let startTime;
    let skipScroll = false;

    $('#navbar').on({
      touchstart(jqueryEvent) {
        const e = jqueryEvent.originalEvent;
        if (!e.changedTouches) {
          return;
        }
        const touchobj = e.changedTouches[0];
        skipScroll = true;
        startX = touchobj.pageX;
        startY = touchobj.pageY;
        startTime = new Date().getTime(); // record time when finger first makes contact with surface
        console.log(touchobj.target.localName);
      },
      touchmove(jqueryEvent) {
        if (skipScroll) {
          jqueryEvent.preventDefault();
        }
      },
      touchend(jqueryEvent) {
        skipScroll = false;
        const e = jqueryEvent.originalEvent;
        const touchobj = e.changedTouches[0];
        const elapsedTime = new Date().getTime() - startTime; // get time elapsed
        const validSwipe = elapsedTime <= allowedTime && Math.abs(touchobj.pageY - startY) > 50 && Math.abs(touchobj.pageX - startX) <= 100;
        if (validSwipe) {
          if ($('#navbar-collapsable').is(':visible') && touchobj.pageY < startY) {
            toggleSearchBar();
            e.preventDefault();
          }
          if (!$('#navbar-collapsable').is(':visible') && touchobj.pageY > startY) {
            toggleSearchBar();
            e.preventDefault();
          }
        }
      },
    });
  }

  componentDidUpdate() {
    // Now scroll back so the navbar is directly at the top of the screen
    // and all of the results start fresh, beneath it
    const normalAffixedTop = $('#navbar-container').offset().top;
    if ($(document).scrollTop() > normalAffixedTop) {
      window.scroll(0, normalAffixedTop);
    }
  }

  filteredClasses() {
    const goodClasses = [];
    const state = this.state;
    this.state.initialClasses.forEach((studioClass) => {
      // Class filtering logic
      if (state.teacher) {
        if (studioClass.name.toLowerCase().indexOf(state.teacher.toLowerCase()) === -1) {
          return;
        }
      }
      if (state.studios.length) {
        if (state.studios.filter(studio => studio === studioClass.location).length === 0) {
          return;
        }
      }
      if (state.styles.length) {
        if (state.styles.filter((searchStyle) => {
          const classHasStyle = studioClass.categories.filter(classStyle => searchStyle === classStyle);
          return classHasStyle.length > 0;
        }).length === 0) {
          return;
        }
      }
      goodClasses.push(studioClass);
    });
    return goodClasses;
  }

  handleUserInput(styles: Array<string>, studios: Array<string>, teacher: string) {
    this.setState({
      styles,
      studios,
      teacher,
    });
  }

  render() {
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
            <table><tbody><tr><td style={{ width: '100%' }}>
              <div id="navbar-collapsable" className="navmenu-height">
                <b>{this.props.location} Street Dance Classes</b>
                <SearchBar
                  initialStudios={this.state.initialStudios}
                  initialStyles={this.state.initialStyles}
                  location={this.props.location}
                  styles={this.state.styles}
                  studios={this.state.studios}
                  teacher={this.state.teacher}
                  onUserInput={this.handleUserInput}
                />
              </div>
              <div id="navbar-collapsed-summary">
                <ClassSummary
                  styles={this.state.styles}
                  studios={this.state.studios}
                  teacher={this.state.teacher}
                />
              </div>
              <DayNavMenu />
            </td><td style={{ verticalAlign: 'bottom' }}>
              <i // eslint-disable-line jsx-a11y/no-static-element-interactions
                id="navbar-collapse-button-icon"
                onClick={toggleSearchBar}
                className="fa fa-caret-square-o-up fa-lg"
              />
            </td></tr></tbody></table>
          </div>
        </div>
        <div>
          <ClassTitle
            filteredClasses={filteredClasses}
          />
          <StudioClasses
            classes={this.state.initialClasses}
            styles={this.state.styles}
            studios={this.state.studios}
            teacher={this.state.teacher}
            filteredClasses={filteredClasses}
          />
          <SponsoredSummary
            classes={this.state.initialClasses}
          />
        </div>
      </div>
    );
  }
}
App.childContextTypes = {
  imagePath: React.PropTypes.string,
};


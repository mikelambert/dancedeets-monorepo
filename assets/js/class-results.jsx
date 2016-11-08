/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */
/* global $ */

'use strict';

import React from 'react';
import dateFormat from 'date-fns/format';

var StudioImage = React.createClass({
  contextTypes: {
    imagePath: React.PropTypes.string,
  },
  render: function() {
    var imageSrc = this.context.imagePath + this.props.studioName.toLowerCase() + '.png';
    return (
      <img src={imageSrc} width="16" height="16" />
    );
  },
});

var SelectButton = React.createClass({
  toggleState: function(e) {
    this.manualToggleState();
    this.props.onChange();
    e.preventDefault();
  },
  manualToggleState: function() {
    var button = $(this.refs.button);
    button.toggleClass('active');
    button.blur();
  },
  isActive: function() {
    return $(this.refs.button).hasClass('active');
  },
  render: function() {
    var extraClass = '';
    if (this.props.value) {
      extraClass = 'active';
    }
    var contents = [];
    if (this.props.thumbnail) {
      contents.push(<StudioImage studioName={this.props.item} />);
    }
    contents.push(this.props.item);

    return (
      <button
        className={'btn btn-default btn-sm ' + extraClass}
        ref="button"
        onClick={this.toggleState}
        >
        {contents}
        </button>
    );
  },
});

var MultiSelectList = React.createClass({
  getValues: function() {
    var values = [];
    var refs = this.refs;
    this.props.list.forEach(function(item, i) {
      if (refs['item' + i].isActive()) {
        values.push(item);
      }
    });
    return values;
  },
  setAll: function() {
    var refs = this.refs;
    this.props.list.forEach(function(item, i) {
      if (refs['item' + i].isActive()) {
        refs['item' + i].manualToggleState();
      }
    });
    // Ensure we leave it active
    if (!this.refs['item-all'].isActive()) {
      this.refs['item-all'].manualToggleState();
    }
    this.props.onChange();
  },
  unsetAll: function() {
    if (this.refs['item-all'].isActive()) {
      this.refs['item-all'].manualToggleState();
    }

    var anySet = false;
    var refs = this.refs;
    this.props.list.forEach(function(item, i) {
      if (refs['item' + i].isActive()) {
        anySet = true;
      }
    });
    if (!anySet) {
      this.refs['item-all'].manualToggleState();
    }

    this.props.onChange();
  },
  render: function() {
    var options = [];
    var emptyList = (this.props.value.length === 0);
    options.push(
      <SelectButton key="All" item="All" ref={'item-all'} value={emptyList} onChange={this.setAll} />
    );
    var thumbnails = this.props.thumbnails;
    var value = this.props.value;
    var unsetAll = this.unsetAll;
    this.props.list.forEach(function(item, i) {
      var subItems = [item];
      if (item.constructor === Array) {
        subItems = item[1];
        item = item[0];
      }

      var selected = true;
      subItems.forEach(function(subItem) {
        selected = selected && (value.indexOf(subItem) !== -1);
      });

      options.push(
        <SelectButton key={item} item={item} ref={'item' + i} value={selected} onChange={unsetAll} thumbnail={thumbnails} />
      );
    });
    return (
      <div className="btn-group" role="group">
      {options}
      </div>
    );
  },
});

function getDayId(dayName) {
  return dayName;
}

var DayLink = React.createClass({
  onClick: function() {
    var id = getDayId(this.props.dayName);
    if ($('#' + id).length === 0) {
      return;
    }
    var scrollOffset = $('#navbar').outerHeight();
    var nudgeOffset = 5;
    $('html, body').animate({scrollTop: $('#' + id).offset().top - scrollOffset - nudgeOffset}, 300);
    // return false; // React does not require that onClick handlers return false
  },
  render: function() {
    return (
      <a href={'#' + getDayId(this.props.dayName)} onClick={this.onClick}>{this.props.dayName}</a>
    );
  },
});

// TODO: i18n?
var dayOfWeekNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

var DayNavMenu = React.createClass({
  render: function() {
    var weeks = [];
    for (var i = 0; i < 7; i++) {
      if (i > 0) {
        weeks.push(<span key={'|-' + i}> | </span>);
      }
      var dayName = dayOfWeekNames[i];
      weeks.push(
        <DayLink
          key={dayName}
          dayName={dayName}
        />
      );
    }
    return (
      <span className="navmenu-height">Jump to:
      {' '}
      {weeks}
      </span>
    );
  },
});

var SearchBar = React.createClass({
  onChange: function() {
    this.props.onUserInput(
        this.refs.styles.getValues(),
        this.refs.studios.getValues(),
        this.refs.teacher.value
    );
  },
  render: function() {
    return (
      <form>
        <div>
          Styles:{' '}
          <MultiSelectList
            list={this.props.initialStyles}
            value={this.props.styles}
            ref="styles"
            onChange={this.onChange}
          />
        </div>
        <div>
          Studios:{' '}
          <MultiSelectList
            list={this.props.initialStudios}
            value={this.props.studios}
            ref="studios"
            onChange={this.onChange}
            thumbnails={true}
          />
        </div>
        <div>
          Teacher:{' '}
          <input
            type="text"
            value={this.props.teacher}
            ref="teacher"
            onChange={this.onChange}
            />
        </div>
      </form>
    );
  },
});

var ClassSummary = React.createClass({
  render: function() {
    var classes = this.props.styles.join(', ');
    if (!classes) {
      classes = 'All';
    }
    var studios = this.props.studios.join(', ');
    if (studios) {
      studios = 'at ' + studios;
    }
    var query = this.props.teacher;
    if (query) {
      query = 'with "' + query + '"';
    }

    return (
      <div>
      {classes} classes {studios} {query}
      </div>
    );
  },
});

var StudioClass = React.createClass({
  render: function() {
    return (
      <div>
        <a href={this.props.studio_class.url}>
        <StudioImage studioName={this.props.studio_class.location} />
        </a>
        {this.props.studio_class.location}: {this.props.studio_class.name}
      </div>
    );
  },
});

var DayHeader = React.createClass({
  render: function() {
    var contents = (
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
  },
});

var TimeHeader = React.createClass({
  render: function() {
    return (
      <b>{dateFormat(this.props.datetime, 'h:mma')}</b>
    );
  },
});

var ClassTitle = React.createClass({
  render: function() {
    var filteredClasses = this.props.filteredClasses;
    return (
      <div><b>Showing {filteredClasses.length} classes:</b></div>
    );
  },
});

var SponsoredSummary = React.createClass({
  render: function() {
    var sponsoredStudios = {};
    this.props.classes.forEach(function(studioClass) {
      var sponsor = studioClass.sponsor;
      if (!(sponsor in sponsoredStudios)) {
        sponsoredStudios[sponsor] = {};
      }
      var studio = studioClass.location;
      sponsoredStudios[sponsor][studio] = true;
    });
    var sponsorHtml = [];
    if ('MINDBODY' in sponsoredStudios) {
      var studioList = Object.keys(sponsoredStudios.MINDBODY);
      sponsorHtml.push(
        <div key="MINDBODY" style={ {margin: '1em 0em', fontStyle: 'italic'} }>
          Studios Powered by <a href="http://www.mindbodyonline.com">MINDBODY</a>:{' '}
          {studioList.join(', ')}
        </div>
      );
    }
    return (
      <div>{sponsorHtml}</div>
    );
  },
});

var StudioClasses = React.createClass({
  render: function() {
    var rows = [];
    var lastStudioClass = null;
    var goodClasses = this.props.filteredClasses;
    var aNamedDays = {};
    goodClasses.forEach(function(studioClass) {
      // Section header rendering
      if (lastStudioClass === null || dateFormat(studioClass.startTime, 'YYYY-MM-DD') !== dateFormat(lastStudioClass.startTime, 'YYYY-MM-DD')) {
        var day = dateFormat(studioClass.startTime, 'dddd');
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
  },
});

function toggleSearchBar() {
  $('#navbar-collapsable').slideToggle('fast');
  var icon = $('#navbar-collapse-button-icon');
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

function parseISO(s) {
  s = s.split(/\D/);
  return new Date(Number(s[0]), Number(s[1]) - 1, Number(s[2]), Number(s[3]), Number(s[4]), Number(s[5]), 0);
}

class App extends React.Component {
  props: {
    imagePath: string,
    searchLocation: string,
    classes: Array<any>;
  };

  constructor(props) {
    super(props);
    const studiosSet = {};
    const stylesSet = {};
    this.props.classes.forEach(function(studioClass) {
      studiosSet[studioClass.location] = true;
      studioClass.categories.forEach(function(category) {
        if (category !== 'All-Styles') {
          stylesSet[category] = true;
        }
      });
    });
    const newClasses = this.props.classes.map(studioClass => {
      const {startTime, ...rest} = studioClass;
      return {startTime: parseISO(startTime), ...rest};
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
  }

  getChildContext() {
    return {imagePath: this.props.imagePath};
  }

  filteredClasses() {
    var goodClasses = [];
    var state = this.state;
    this.state.initialClasses.forEach(function(studioClass) {
      // Class filtering logic
      if (state.teacher) {
        if (studioClass.name.toLowerCase().indexOf(state.teacher.toLowerCase()) === -1) {
          return;
        }
      }
      if (state.studios.length) {
        if (state.studios.filter(function(studio) {
          return studio === studioClass.location;
        }).length === 0) {
          return;
        }
      }
      if (state.styles.length) {
        if (state.styles.filter(function(searchStyle) {
          var classHasStyle = studioClass.categories.filter(function(classStyle) {
            return searchStyle === classStyle;
          });
          return classHasStyle.length > 0;
        }).length === 0) {
          return;
        }
      }
      goodClasses.push(studioClass);
    });
    return goodClasses;
  }

  handleUserInput(styles, studios, teacher) {
    this.setState({
      styles: styles,
      studios: studios,
      teacher: teacher,
    });
  }

  componentDidMount() {
    var allowedTime = 500; // maximum time allowed to travel that distance
    var startX;
    var startY;
    var startTime;
    var skipScroll = false;

    $('#navbar').on({
      touchstart: function(jqueryEvent) {
        var e = jqueryEvent.originalEvent;
        if (!e.changedTouches) {
          return;
        }
        var touchobj = e.changedTouches[0];
        skipScroll = true;
        startX = touchobj.pageX;
        startY = touchobj.pageY;
        startTime = new Date().getTime(); // record time when finger first makes contact with surface
        console.log(touchobj.target.localName);
      },
      touchmove: function(jqueryEvent) {
        if (skipScroll) {
          jqueryEvent.preventDefault();
        }
      },
      touchend: function(jqueryEvent) {
        skipScroll = false;
        var e = jqueryEvent.originalEvent;
        var touchobj = e.changedTouches[0];
        var elapsedTime = new Date().getTime() - startTime; // get time elapsed
        var validSwipe = elapsedTime <= allowedTime && Math.abs(touchobj.pageY - startY) > 50 && Math.abs(touchobj.pageX - startX) <= 100;
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
    var normalAffixedTop = $('#navbar-container').offset().top;
    if ($(document).scrollTop() > normalAffixedTop) {
      window.scroll(0, normalAffixedTop);
    }
  }

  render() {
    var filteredClasses = this.filteredClasses();
    return (
      <div>
        <div
          id="navbar-container"
          style={ {
            marginBottom: '1em',
          } }
          >
          <div
            id="navbar"
            style={ {
              backgroundColor: 'white',
              boxShadow: '0 5px 4px -4px black',
              zIndex: 50,
            } }
          >
            <table><tbody><tr><td style={ {width: '100%'} }>
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
            </td><td style={ {verticalAlign: 'bottom'} }>
              <i
              id="navbar-collapse-button-icon"
              onClick={toggleSearchBar}
              className="fa fa-caret-square-o-up fa-lg"></i>
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

module.exports = App;

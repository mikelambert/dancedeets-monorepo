
var SelectButton = React.createClass({
  toggleState: function() {
    this.manualToggleState();
    this.props.onChange();
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
    return (
      <a
        className={"btn btn-default btn-sm " + extraClass}
        ref="button"
        href="javascript:void(0);"
        onClick={this.toggleState}
        >
          {this.props.item}
        </a>
    );
  }
});

var MultiSelectList = React.createClass({
  getValues: function() {
    var values = [];
    var refs = this.refs;
    this.props.list.forEach(function(item, i) {
      if (refs['item'+i].isActive()) {
        values.push(item);
      }
    });
    return values;
  },
  setAll: function() {
    var values = [];
    var refs = this.refs;
    this.props.list.forEach(function(item, i) {
      if (refs['item'+i].isActive()) {
        refs['item'+i].manualToggleState();
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
      if (refs['item'+i].isActive()) {
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
    var emptyList = (this.props.value.length == 0);
    options.push(
      <SelectButton key="All" item="All" ref={'item-all'} value={emptyList} onChange={this.setAll} />
    );
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
        selected = selected && ($.inArray(subItem, value) != -1);
      });

      options.push(
        <SelectButton key={item} item={item} ref={'item'+i} value={selected} onChange={unsetAll} />
      );
    });
    return (
      <div className="btn-group" role="group">
      {options}
      </div>
    );
  }
});

function getDayId(dayName) {
    return dayName;
}

var DayLink = React.createClass({
  onClick: function() {
    var id = getDayId(this.props.dayName);
    var scrollOffset = $('#navbar').outerHeight();
    var nudgeOffset = 5;
    $("html, body").animate({ scrollTop: $('#'+id).offset().top - scrollOffset - nudgeOffset }, 300);
    // return false; // React does not require that onClick handlers return false
  },
  render: function() {
    return (
      <a href={'#'+getDayId(this.props.dayName)} onClick={this.onClick}>{this.props.dayName}</a>
    );
  }
});

var DayNavMenu = React.createClass({
  render: function() {
    var weeks = [];
    for (var i = 0; i < 7; i++) {
      if (i > 0) {
        weeks.push(<span key={'|-'+i}> | </span>);
      }
      var dayName = moment().weekday(i).format("ddd");
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
  }
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
    var missingDiv = null;
    if (this.props.location == 'Los Angeles, CA') {
      missingDiv = (
        <div><i>Currently Missing:{' '}
          <a href="https://clients.mindbodyonline.com/classic/home?studioid=133521">mL</a>,{' '}
          <a href="https://clients.mindbodyonline.com/classic/home?studioid=110557">Quest Studio</a>
        </i></div>
      );
    }
    return (
      <form>
        <div>
          Styles:{' '}
          <MultiSelectList
            list={this.props.initial_styles}
            value={this.props.styles}
            ref="styles"
            onChange={this.onChange}
          />
        </div>
        <div>
          Studios:{' '}
          <MultiSelectList
            list={this.props.initial_studios}
            value={this.props.studios}
            ref="studios"
            onChange={this.onChange}
          />
        </div>
        {missingDiv}
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
  }
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
  }
});

var StudioClass = React.createClass({
  render: function() {
    return (
      <div>
        <a href={this.props.studio_class.url}>
        {this.props.studio_class.location}: {this.props.studio_class.name}
        </a>
      </div>
    );
  }
});

var DayHeader = React.createClass({
  render: function() {
    var contents = (
      <h4>{this.props.date.format("ddd MMM D")}</h4>
    );
    if (this.props.useAnchor) {
      contents = (
        <div id={getDayId(this.props.date.format("ddd"))}>
          {contents}  
        </div>
      );
    }
    return contents;
  }
});

var TimeHeader = React.createClass({
  render: function() {
    return (
      <b>{this.props.datetime.format("h:mma")}</b>
    );
  }
});

var ClassTitle = React.createClass({
  render: function() {
    var filteredClasses = this.props.filteredClasses;
    return (
      <div><b>Showing {filteredClasses.length} classes:</b></div>
    );
  }
});

var SponsoredSummary = React.createClass({
  render: function() {
    var sponsoredStudios = {}
    this.props.classes.forEach(function(studio_class) {
      var sponsor = studio_class['sponsor'];
      if (!(sponsor in sponsoredStudios)) {
        sponsoredStudios[sponsor] = {};
      }
      var studio = studio_class['location'];
      sponsoredStudios[sponsor][studio] = true;
    });
    var sponsorHtml = [];
    if ('MINDBODY' in sponsoredStudios) {
      var studioList = Object.keys(sponsoredStudios['MINDBODY']);
      sponsorHtml.push(
        <div key='MINDBODY' style={ {margin: '1em 0em', fontStyle: 'italic'} }>
          Studios Powered by <a href="http://www.mindbodyonline.com">MINDBODY</a>:{' '}
          {studioList.join(', ')}
        </div>
      );
    }
    return (
      <div>{sponsorHtml}</div>
    );
  }
});

var StudioClasses = React.createClass({
  render: function() {
    var rows = [];
    var last_studio_class = null;
    var props = this.props;
    var goodClasses = this.props.filteredClasses;
    var aNamedDays = {};
    goodClasses.forEach(function(studio_class) {
      // Section header rendering
      if (last_studio_class == null || studio_class.start_time.format("YYYY-MM-DD") != last_studio_class.start_time.format("YYYY-MM-DD")) {
        var day = studio_class.start_time.format("ddd");
        rows.push(
          <DayHeader
            date={studio_class.start_time}
            key={studio_class.start_time.format("YYYY-MM-DD")}
            useAnchor={!aNamedDays[day]}
          />
        );
        aNamedDays[day] = true;
      }
      if (last_studio_class == null || studio_class.start_time.format("HH:mm") != last_studio_class.start_time.format("HH:mm")) {
        rows.push(<TimeHeader datetime={studio_class.start_time} key={studio_class.start_time.format("YYYY-MM-DDTHH:mm")} />);
      }
      // Class rendering
      rows.push(<StudioClass studio_class={studio_class} key={studio_class.key} />);
      last_studio_class = studio_class;
    });
    return <div>{rows}</div>;
  }
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


var App = React.createClass({
  filteredClasses: function() {
    var goodClasses = [];
    var props = this.state;
    this.props.classes.forEach(function(studio_class) {
      // Class filtering logic
      if (props.teacher) {
        if (studio_class.name.toLowerCase().indexOf(props.teacher.toLowerCase()) == -1) {
          return;
        }
      }
      if (props.studios.length) {
        if (props.studios.filter(function(studio) {
          return studio == studio_class.location;
        }).length == 0) {
          return;
        }
      }
      if (props.styles.length) {
        if (props.styles.filter(function(search_style) {
          var classHasStyle = studio_class.categories.filter(function(class_style) {
            return search_style == class_style;
          });
          return classHasStyle.length > 0;
        }).length == 0) {
          return;
        }
      }
      goodClasses.push(studio_class);
    });
    return goodClasses;
  },
  getInitialState: function() {
    return {
        styles: [],
        studios: [],
        teacher: ''
    };
  },
  handleUserInput: function(styles, studios, teacher) {
    this.setState({
      styles: styles,
      studios: studios,
      teacher: teacher
    });
  },
  componentDidMount: function componentDidMount() {
    var allowedTime = 500; // maximum time allowed to travel that distance
    var startX;
    var startY;
    var startTime;
    var skipScroll = false;

    $('#navbar').on({
      'touchstart' : function (jqueryEvent) {
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
      'touchmove' : function (jqueryEvent) {
        if (skipScroll) {
          jqueryEvent.preventDefault();
        }
      },
      'touchend' : function (jqueryEvent) {
        skipScroll = false;
        var e = jqueryEvent.originalEvent;
        var touchobj = e.changedTouches[0];
        var dist = touchobj.pageY - startY; // get total dist traveled by finger while in contact with surface
        var elapsedTime = new Date().getTime() - startTime; // get time elapsed
        var validSwipe = elapsedTime <= allowedTime && Math.abs(touchobj.pageY - startY) > 50 && Math.abs(touchobj.pageX - startX) <= 100;
        if (validSwipe) {
          if ($('#navbar-collapsable').is(":visible") && touchobj.pageY < startY) {
            toggleSearchBar();
            e.preventDefault();
          }
          if (!$('#navbar-collapsable').is(":visible") && touchobj.pageY > startY) {
            toggleSearchBar();
            e.preventDefault();
          }
        }
      }
    });
  },
  componentDidUpdate: function() {
    // Now scroll back so the navbar is directly at the top of the screen
    // and all of the results start fresh, beneath it
    var normalAffixedTop = $('#navbar-container').offset().top;
    if ($(document).scrollTop() > normalAffixedTop) {
      window.scroll(0, normalAffixedTop);
    }
  },
  render: function() {
    var filteredClasses = this.filteredClasses()
    return (
      <div>
        <div
          id="navbar-container"
          style={ {
            marginBottom: "1em"
            } }
          >
          <div
            id="navbar"
            style={ {
              backgroundColor: "white",
              boxShadow: "0 5px 4px -4px black",
              } }
          >
            <table><tbody><tr><td style={ {width: '100%'} }>
              <div id="navbar-collapsable" className="navmenu-height">
                <b>{this.props.location} Street Dance Classes</b>
                <SearchBar
                  initial_studios={this.props.studios}
                  initial_styles={this.props.styles}
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
            </td><td style={ { verticalAlign: 'bottom' } }>
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
            classes={this.props.classes}
            styles={this.state.styles}
            studios={this.state.studios}
            teacher={this.state.teacher}
            filteredClasses={filteredClasses}
          />
          <SponsoredSummary
            classes={this.props.classes}
          />
        </div>
      </div>
    )
  }
});

ReactDOM.render(
  <App
    location={searchLocation}
    classes={classes}
    studios={studios}
    styles={styles}
  />,
  document.getElementById('app')
);

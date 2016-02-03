global.jQuery = global.$ = require('jquery');
require('jquery.backstretch');
require('bootstrap');
var App = require('./app');

// From old site: jquery.cookie@1.4.1,momentjs@2.10.6,jquery.lazyload@1.9.3

$(document).ready(function() {
  App.init()

  // background-image rotation
  var images = [
    'dist/img/background-show-locking.jpg',
    'dist/img/background-class-overhead.jpg',
    'dist/img/background-club-turntable.jpg',
    'dist/img/background-show-awards.jpg',

    'dist/img/background-class-kids.jpg',
    'dist/img/background-show-pose.jpg',
    'dist/img/background-club-smoke-cypher.jpg',
    'dist/img/background-class-rocking.jpg',
    'dist/img/background-club-hustle.jpg',
    'dist/img/background-show-dj.jpg',
    'dist/img/background-club-headspin.jpg',
  ];
  if ($(document).width() > 900) {
    images = images.map(function(x) {
      return x.replace('.jpg', '@2x.jpg');
    });
  }
  $('.fullscreen-static-image').backstretch(images, {duration: 8000, fade: 1500});

  // animate-on-hover
  $('.animate-on-hover').hover(function() {
    $(this).addClass('animated ' + $(this).data('action'));
  });
  $('.animate-on-hover').bind('animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd', function() {
    $(this).removeClass('animated ' + $(this).data('action'));
  });
});

global.jQuery = global.$ = require('jquery');
require('jquery.backstretch');
require('bootstrap');
var WOW = require('wow.js');
var App = require('./app');

//from old site: jquery.cookie@1.4.1,momentjs@2.10.6,jquery.lazyload@1.9.3

jQuery(document).ready(function() {
    App.init()
    new WOW.WOW().init(live=false);

    // background-image rotation
    $(".fullscreen-static-image").backstretch([
        "dist/img/background-show-locking.jpg",
        "dist/img/background-class-overhead.jpg",
        "dist/img/background-club-turntable.jpg",
        "dist/img/background-show-awards.jpg",

        "dist/img/background-class-kids.jpg",
        "dist/img/background-show-pose.jpg",
        "dist/img/background-club-smoke-cypher.jpg",
        "dist/img/background-class-rocking.jpg",
        "dist/img/background-club-hustle.jpg",
        "dist/img/background-show-dj.jpg",
        "dist/img/background-club-headspin.jpg",

    ], {duration: 4000, fade: 800});

    // animate-on-hover
    $(".animate-on-hover").hover(function(){
        $(this).addClass('animated ' + $(this).data('action'));
    });
    $(".animate-on-hover").bind("animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd",function(){
        $(this).removeClass('animated ' + $(this).data('action'));
    });
});



require('jquery')
require('jquery-backstretch')

require('bootstrap')
var WOW = require('wow')
var App = require('./assets/js/app')

//<!--from old site: jquery.cookie@1.4.1,momentjs@2.10.6,jquery.lazyload@1.9.3-->

jQuery(document).ready(function() {
    App.init()
    new WOW.WOW().init(live=false);

    // background-image rotation
    $(".fullscreen-static-image").backstretch([
        "assets/img/header-boty.jpg",
        "assets/img/header-bay-choreo.jpg",
    ], {duration: 4000, fade: 800});

    // animate-on-hover
    $(".animate-on-hover").hover(function(){
        $(this).addClass('animated ' + $(this).data('action'));
    });
    $(".animate-on-hover").bind("animationend webkitAnimationEnd oAnimationEnd MSAnimationEnd",function(){
        $(this).removeClass('animated ' + $(this).data('action'));
    });
});



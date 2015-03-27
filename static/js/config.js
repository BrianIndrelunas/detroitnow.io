requirejs.config({
    baseUrl: "/static",
    shim:{
        "jquery": {
            "exports": "jQuery"
        },
        "bootstrap": {
            "deps": ["jquery"]
        },
        "epoch": {
            "deps": ["d3", "jquery"]
        },
        "animateNumber": {
            "deps": ["jquery"]
        },
        "jquery.shuffle.modernizr":{
            "deps": ["jquery", "modernizr"]
        },
        "modernizr": {
            "exports": "Modernizr"
        }
    },
    paths: {
        "base": "js/base",
        "init": "js/init",
        "jquery": "//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min",
        "leaflet": "bower_components/leaflet/dist/leaflet",
        "handlebars": "bower_components/handlebars/handlebars",
        "bootstrap": "//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min",
        "d3": "bower_components/d3/d3.min",
        "epoch": "bower_components/epoch/epoch.min",
        "animateNumber": "lib/jquery.animateNumber.min",
        "colorbrewer": "bower_components/colorbrewer2/colorbrewer",
        "jquery.shuffle.modernizr": "bower_components/shufflejs/dist/jquery.shuffle.modernizr",
        "modernizr": "bower_components/shufflejs/dist/modernizr.custom.min",
        "c3": "bower_components/c3/c3",
    }
});
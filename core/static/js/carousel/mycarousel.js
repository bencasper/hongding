$(document).ready(function () {
    var carousel = $("#carousel").waterwheelCarousel({
        flankingItems: 3,
        movingToCenter: function ($item) {
            $('#callback-output').prepend('movingToCenter: ' + $item.attr('id') + '<br/>');
        },
        movedToCenter: function ($item) {
            $('#callback-output').prepend('movedToCenter: ' + $item.attr('id') + '<br/>');
        },
        movingFromCenter: function ($item) {
            $('#callback-output').prepend('movingFromCenter: ' + $item.attr('id') + '<br/>');
        },
        movedFromCenter: function ($item) {
            $('#callback-output').prepend('movedFromCenter: ' + $item.attr('id') + '<br/>');
        },
        clickedCenter: function ($item) {
            $('#callback-output').prepend('clickedCenter: ' + $item.attr('id') + '<br/>');
        }
    });

    $('#lbt').bind('click', function () {
        carousel.next();
        return false
    });

    $('#rbt').bind('click', function () {
        carousel.prev();
        return false;
    });

    setInterval(function () {
        carousel.next();
        return false;
    }, 3000);

});

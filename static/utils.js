function toggle_bool(name) {
    if ($.cookie(name) == 1) {
        newval = 0;
    } else {
        newval = 1;
    }
    $.cookie(name, newval, {expires: 180, path: '/'});
    location.reload();
    return false;
}

function showBefore(event) {
    var e = $('ul.hide-excess');
    var h = e.height();
    e.css('height', 'auto');
    e.css('max-height', h);
    e.css('overflow-x', 'hidden');
    e.removeClass('hide-before');
    e.addClass('show-before');
    event.stopPropagation();
}

function showAfter(event) {
    var e = $('ul.hide-excess');
    var h = e.height();
    e.css('max-height', h);
    e.css('overflow-x', 'hidden');
    e.removeClass('hide-after');
    e.addClass('show-after');
    event.stopPropagation();
}

$(function () {
    var e = $('ul.hide-excess');
    e.removeClass('show-before');
    e.removeClass('show-after');
    e.addClass('hide-before');
    e.addClass('hide-after');

    $('li.ldots-before>a').click(showBefore);
    $('li.ldots-after>a').click(showAfter);
})

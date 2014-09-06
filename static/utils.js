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

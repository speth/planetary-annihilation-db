function toggle_commander_variants() {
    if ($.cookie("show_commander_variants") == 1) {
        newval = 0;
    } else {
        newval = 1;
    }
    $.cookie("show_commander_variants", newval, {expires: 180, path: '/'});
    location.reload();
    return false;
}

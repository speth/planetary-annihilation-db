import units
import tarfile
import os

def save_db_info(pa_root=None, version=None):
    if pa_root:
        units.CONFIG['pa_root'] = pa_root
    else:
        pa_root = units.CONFIG['pa_root']

    db = units.VersionDb()
    db.load_units()

    if version is None:
        version = open(pa_root +'/../version.txt').read().strip()

    archive_root = 'units-' + version
    archive_name = 'units-{}.tar.bz2'.format(version)
    print('Creating archive: "{}"'.format(archive_name))

    with tarfile.open(archive_name, 'w:bz2') as archive:
        archive.add(pa_root + '/pa/units/unit_list.json',
                    arcname=archive_root + '/pa/units/unit_list.json')

        for filename in db._things:
            if os.path.exists(pa_root + filename):
                archive.add(pa_root + filename,
                            arcname=archive_root + filename)
            else:
                print('WARNING: missing file {!r}'.format(filename))

        path_tmpl = '/ui/{}/live_game/img/build_bar/units/{}.png'
        for unit in db.units.values():
            for directory in ('main/game', 'alpha'):
                iconpath = path_tmpl.format(directory, unit.safename)
                if os.path.exists(pa_root + iconpath):
                    archive.add(pa_root + iconpath,
                                arcname=archive_root + iconpath)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        save_db_info()
    elif len(sys.argv) <= 3:
        save_db_info(*sys.argv[1:])
    else:
        print('Unrecognized command line arguments:', repr(sys.argv[1:]))
        sys.exit(1)

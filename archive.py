import units
import tarfile
import os

def save_db_info(archive_name):
    pa_root = units.CONFIG['pa_root']
    archive_root = 'padb-data'
    db = units.VersionDb()
    db.load_units()

    with tarfile.open(archive_name, 'w:bz2') as archive:
        archive.add(pa_root + '/pa/units/unit_list.json',
                    arcname=archive_root + '/pa/units/unit_list.json')

        for filename in db._things:
            archive.add(pa_root + filename,
                        arcname=archive_root + filename)

        path_tmpl = '/ui/{}/live_game/img/build_bar/units/{}.png'
        for unit in db.units.values():
            for directory in ('main/game', 'alpha'):
                iconpath = path_tmpl.format(directory, unit.safename)
                if os.path.exists(pa_root + iconpath):
                    archive.add(pa_root + iconpath,
                                arcname=archive_root + iconpath)

if __name__ == '__main__':
    import sys
    save_db_info(sys.argv[1])

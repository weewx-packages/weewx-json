import json
import shutil
from pathlib import Path

import configobj
import pytest
import weewx
import weewx.manager
import weewx.reportengine
import weewx.station


@pytest.mark.parametrize('extended', [False, True])
def test_real_reports(tmp_path, extended):
    root = Path(__file__).parents[1]
    shutil.copytree(root / 'skins', tmp_path / 'skins')
    config = configobj.ConfigObj({
        'WEEWX_ROOT': str(tmp_path),
        'Station': {'latitude': '40', 'longitude': '-70', 'altitude': ['10', 'meter'],
                    'location': 'Test "station" \\ Berlin', 'station_url': 'https://example.test'},
        'StdReport': {'SKIN_ROOT': 'skins', 'HTML_ROOT': 'public_html',
                      'data_binding': 'wx_binding', 'JSONReport': {'skin': 'JSON', 'enable': True}},
        'DataBindings': {'wx_binding': {'database': 'archive', 'table_name': 'archive',
                         'manager': 'weewx.manager.DaySummaryManager'}},
        'Databases': {'archive': {'database_name': str(tmp_path / 'weather.sdb'), 'driver': 'weedb.sqlite'}}})
    fields = [('dateTime', 'INTEGER NOT NULL UNIQUE PRIMARY KEY'), ('usUnits', 'INTEGER'),
              ('interval', 'INTEGER'), ('outTemp', 'REAL'), ('outHumidity', 'REAL')]
    if extended:
        fields += [(name, 'REAL') for name in ['UV', 'radiation', 'pm2_5', 'pm10_0', 'co2', 'soilMoist1']]
    config['DataBindings']['wx_binding']['schema'] = dict(fields)
    timestamp = 1720000200
    with weewx.manager.open_manager_with_config(config, 'wx_binding', initialize=True) as database:
        for i in range(24):
            record = {'dateTime': timestamp - (23-i)*300, 'usUnits': weewx.METRICWX,
                      'interval': 5, 'outTemp': 0.0, 'outHumidity': 0.0}
            if extended:
                record.update(UV=0.0, radiation=0.0, pm2_5=3.5, pm10_0=None, co2=420.0, soilMoist1=10.0)
            database.addRecord(record)
    station = weewx.station.StationInfo(**config['Station'])
    weewx.reportengine.StdReportEngine(config, station, gen_ts=timestamp).run()
    full = json.loads((tmp_path / 'public_html/weewx.json').read_text())
    minimal = json.loads((tmp_path / 'public_html/current_minimal.json').read_text())
    for report in [full, minimal]:
        assert report['station']['location'] == 'Test "station" \\ Berlin'
        assert report['current']['temperature']['value'] == 32.0
        assert report['current']['temperature']['units'] == '°F'
        if extended:
            assert report['current']['uv index']['value'] == 0.0
            assert report['current']['radiation']['value'] == 0.0
            assert report['current']['pm2_5']['value'] == 3.5
            assert report['current']['co2']['value'] == 420.0
            assert 'pm10_0' not in report['current']
        else:
            assert 'uv index' not in report['current']
            assert 'pm2_5' not in report['current']
    if extended:
        for period in ['day', 'week', 'month', 'year']:
            assert full[period]['max uv index']['value'] == 0.0
            assert full[period]['min radiation']['value'] == 0.0

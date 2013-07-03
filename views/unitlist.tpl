<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>PADB - Unit List</title>
    <link rel="stylesheet" href="/static/site.css">
  </head>
  <body>
    <table>
    <tr>
        <th>Name</th>
        <th>HP</th>
        <th>DPS</th>
        <th>salvo</th>
        <th>cost</th>
    </tr>
    % for u in units:
    <tr>
        <td>{{u.role}}</td>
        <td class="num">{{u.health}}</td>
        <td class="num">{{u.dps}}</td>
        <td class="num">{{u.salvo_damage}}</td>
        <td class="num">{{u.build_cost}}</td>
    </tr>
    % end
    </table>
  </body>
</html>

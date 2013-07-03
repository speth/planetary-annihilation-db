
<table border=1 cellpadding=5 cellspacing=0>
<tr>
    <td>Name</td>
    <td>HP</td>
    <td>DPS</td>
    <td>salvo</td>
    <td>cost</td>
</tr>
% for u in units:
<tr>
    <td>{{u.role}}</td>
    <td>{{u.health}}</td>
    <td>{{u.dps}}</td>
    <td>{{u.salvo_damage}}</td>
    <td>{{u.build_cost}}</td>
</tr>
% end
</table>

<span class="tier">T{{unit.tier}}</span>
  % if version == 'current':
	<a href="/unit/{{unit.safename}}">
  % else:
    <a href="/unit/{{unit.safename}}?version={{version}}">
  % end
  % if unit.name == unit.role:
    {{unit.name}}
  % else:
    {{unit.role}}: <em>{{unit.name}}</em>
  % end
</a>

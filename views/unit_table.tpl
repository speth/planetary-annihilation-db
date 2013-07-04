<table>
  % if caption:
  <caption>{{caption}}</caption>
  % end
  <tr>
  % for name in columns:
    <th>{{name}}</th>
  % end
  </tr>
  % for row in data:
  <tr>
    <td>
    % u = row[0]
    <a href="/unit/{{u.safename}}">
    % if u.name == u.role:
    {{u.name}}
    % else:
    {{u.role}}: <em>{{u.name}}</em>
    % end
    </a></td>

    % for item in row[1:]:
    <td class="num">{{item}}</td>
    % end
  </tr>
  % end
</table>

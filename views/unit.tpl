<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>PADB - {{u.name}}</title>
    <link rel="stylesheet" href="/static/site.css">
  </head>
  <body>
    % if u.name == u.role:
    <h1>{{u.name}}</h1>
    % else:
    <h1>{{u.role}}: <em>{{u.name}}</em></h1>
    % end
    {{u.description}}
    <ul>
      <li>HP: {{u.health}}</li>
      <li>Build cost: {{u.build_cost}} metal</li>
      <li>Built by:
        <ul>
          % for other in u.built_by:
          <li> <a href="/unit/{{other.webname}}">
          % if other.name == other.role:
          {{other.name}}
          % else:
          {{other.role}}: <em>{{other.name}}</em>
          % end
          </a></li>
          % end
        </ul>
      </li>
      % if u.builds:
      <li>Builds:
        <ul>
          % for other in u.builds:
          <li><a href="/unit/{{other.webname}}">
          % if other.name == other.role:
          {{other.name}}
          % else:
          {{other.role}}: <em>{{other.name}}</em>
          % end
          </a></li>
          % end
        </ul>
      </li>
      % end
    </ul>
  </body>
</html>

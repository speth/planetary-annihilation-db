<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>PADB</title>
    <link rel="stylesheet" href="/static/site.css">
  </head>
  <body>
    % include nav_bar
    <div class="content">
      % for table in tables:
        {{!table}}
      % end
    </div>
  </body>
</html>

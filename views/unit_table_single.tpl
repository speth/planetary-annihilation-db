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
      % include unit_table caption=caption, columns=columns, data=data
    </div>
  </body>
</html>

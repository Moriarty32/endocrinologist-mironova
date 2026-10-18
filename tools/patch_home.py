# -*- coding: utf-8 -*-
import io
import re

path = "index.html"
s = io.open(path, encoding="utf-8").read()
s = re.sub(r'  <header class="site-header ref-header".*?</header>', '  <div id="site-header"></div>', s, count=1, flags=re.S)
s = re.sub(r'  <footer class="site-footer ref-footer">.*?</footer>', '  <div id="site-footer"></div>', s, count=1, flags=re.S)
s = s.replace("<body>", '<body data-base="">', 1)
s = s.replace(
    '  <link rel="stylesheet" href="landing.css?v=20261018i">',
    '  <link rel="stylesheet" href="landing.css?v=20261018i">\n  <link rel="stylesheet" href="site.css?v=20261019a">',
    1,
)
s = s.replace(
    '  <script src="app.js?v=20261018c" defer></script>',
    '  <script src="assets/js/site-data.js?v=20261019a" defer></script>\n'
    '  <script src="assets/js/site.js?v=20261019a" defer></script>\n'
    '  <script src="app.js?v=20261019a" defer></script>',
    1,
)
io.open(path, "w", encoding="utf-8").write(s)
print("home shell replaced", len(s))

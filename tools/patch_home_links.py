# -*- coding: utf-8 -*-
import io

p = "index.html"
s = io.open(p, encoding="utf-8").read()
s = s.replace("\\n", "\n")
old = '''<a class="btn btn-outline" href="#booking">Записаться на повторную</a>
          </article>
        </div>'''
new = '''<a class="btn btn-outline" href="#booking">Записаться на повторную</a>
          </article>
        </div>
        <p class="ref-head-link"><a href="ceny/">Все цены и условия <svg class="icon" aria-hidden="true"><use href="assets/icons.svg?v=20261018d#icon-arrow-right"></use></svg></a></p>'''
if old in s:
    s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("home links fixed")

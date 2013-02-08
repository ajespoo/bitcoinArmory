import gettxcolor as g

# Substitute in your own transactions and expected colors

#g.DEBUG = True

print g.search_for_color('3a60b70d425405f3e45f9ed93c30ca62b2a97e692f305836af38a524997dd01d',0), "== None (Random TX from blockchain)"
print g.search_for_color('c1d8d2fb75da30b7b61e109e70599c0187906e7610fe6b12c58eecc3062d1da5',0), "== Red"
print g.search_for_color('8f6c8751f39357cd42af97a67301127d497597ae699ad0670b4f649bd9e39abf',0), "== Red"
print g.search_for_color('f50f29906ce306be3fc06df74cc6a4ee151053c2621af8f449b9f62d86cf0647',0), "== Blue"
print g.search_for_color('7e40d2f414558be60481cbb976e78f2589bc6a9f04f38836c18ed3d10510dce5',0), "== Blue"
print g.search_for_color('4b60bb49734d6e26d798d685f76a409a5360aeddfddcb48102a7c7ec07243498',0), "== Red (Two-input merging TX)"
print g.search_for_color('342f119db7f9989f594d0f27e37bb5d652a3093f170de928b9ab7eed410f0bd1',0), "== None (Color mixing TX)"
print g.search_for_color('bd34141daf5138f62723009666b013e2682ac75a4264f088e75dbd6083fa2dba',0), "== Blue (complex chain TX)"
print g.search_for_color('bd34141daf5138f62723009666b013e2682ac75a4264f088e75dbd6083fa2dba',1), "== None (mining fee change output)"
print g.search_for_color('36af9510f65204ec5532ee62d3785584dc42a964013f4d40cfb8b94d27b30aa1',0), "== Red (complex chain TX)"

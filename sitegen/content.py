# -*- coding: utf-8 -*-
# Carga la configuracion y los articulos desde JSON (editable por la automatizacion).
import json, os
_d = os.path.dirname(os.path.abspath(__file__))
CONFIG = json.load(open(os.path.join(_d, "config.json"), encoding="utf-8"))
ARTICLES = json.load(open(os.path.join(_d, "articles.json"), encoding="utf-8"))

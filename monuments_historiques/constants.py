#!/usr/bin/env python3
#
#  constants.py
"""
String constants.
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# 3rd party
from nhle_map.constants import Dataset
from nhle_map.icons import FontawesomeLayerIcon

__all__ = [
		"LAYERS",
		"MAX_LAT",
		"MAX_LNG",
		"MIN_LAT",
		"MIN_LNG",
		"MONUMENTS_HISTORIQUES",
		]

MONUMENTS_HISTORIQUES = Dataset(
		variable_prefix="monumentsHistoriques",
		identifier="monuments_historiques",
		name="Monuments Historiques",
		noun="Monument Historique",
		icon=FontawesomeLayerIcon(icon="monument", marker_colour="#006fb2", svg_marker=True),
		geojson_filename="Monuments Historiques.geojson",
		)

LAYERS = [MONUMENTS_HISTORIQUES]

MIN_LAT = -26
MIN_LNG = -68
MAX_LAT = 52
MAX_LNG = 66

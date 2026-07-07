#!/usr/bin/env python3
#
#  map.py
"""
Map generation.
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
import folium
from domdf_folium_tools import markercluster
from domdf_folium_tools.elements import LocateControl, add_to, set_id
from folium_about_button import AboutControl
from folium_map_search import MapSearchControl, MapSearchProvider
from folium_map_swap_control import MapSwapControl
from folium_zoom_state import OverlayState, ZoomStateJS
from nhle_map.map import LayerControl, Map, MarkerGroup, MarkerLoadingJS

# this package
from monuments_historiques import constants

__all__ = ["make_map"]


def make_map() -> folium.Map:
	"""
	Make the listed buildings folium map.
	"""

	MAX_ZOOM = 20

	osm_tiles = set_id(
			folium.TileLayer(
					tiles="OpenStreetMap",
					name="OpenStreetMap",
					# show=False,
					control=False,
					max_zoom=MAX_ZOOM,
					max_native_zoom=19,
					referrerPolicy="strict-origin-when-cross-origin",
					attr='Map &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
					),
			"osm_carto",
			)

	m = Map(
			location=(46.7692, 2.4442),
			minZoom=6,
			maxZoom=MAX_ZOOM,
			zoom_start=9,
			wheelPxPerZoomLevel=80,
			tiles=osm_tiles,
			control_scale=True,  # prefer_canvas=True,
			# max_bounds=True,
			# min_lat=constants.MIN_LAT - 2,
			# min_lon=constants.MIN_LNG - 2,
			# max_lat=constants.MAX_LAT + 2,
			# max_lon=constants.MAX_LNG + 3,
			)

	# set_id(os25inch, "os25inch").add_to(m)

	# preloads = Preload()
	# # preloads.add_preload("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/images/marker-icon.png", "image")
	# # preloads.add_preload("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/images/marker-icon-2x.png", "image")
	# # preloads.add_preload("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/images/marker-shadow.png", "image")
	# preloads.add_preload("https://unpkg.com/leaflet-extra-markers@1.2.2/dist/img/markers_default.png", "image")
	# preloads.add_preload("https://unpkg.com/leaflet-extra-markers@1.2.2/dist/img/markers_shadow.png", "image")
	# preloads.add_to(m)

	mcg = markercluster.MarkerCluster(
			chunkedLoading=True,
			chunk_progress_function="updateProgressBar",
			max_cluster_radius_function="getClusterRadius",
			control=False,
			show=False,
			)
	add_to(mcg, m, "nhle")

	layer: constants.Dataset
	for layer in constants.LAYERS:
		marker_group = MarkerGroup(
				cluster=mcg,
				name=layer.layer_label,
				layer_control_colour=layer.icon.marker_colour,
				)
		add_to(marker_group, m, layer.identifier)

	MarkerLoadingJS(layers=constants.LAYERS).add_to(m)
	ZoomStateJS().add_to(m)
	LocateControl().add_to(m)
	AboutControl("aboutModal").add_to(m)
	search_provider = MapSearchProvider(
			layer=mcg,
			map=m,
			# viewbox=f"{constants.MIN_LNG},{constants.MIN_LAT},{constants.MAX_LNG},{constants.MAX_LAT}",
			feature_type="settlement",
			)
	MapSearchControl(
			provider=search_provider,
			auto_complete_delay=1000,  # Effectively turns off autocomplete to comply with Nominatum TOS
			show_marker=False,
			max_suggestions=15,
			search_label="Enter town or list entry name",
			disable_enter_search=True,  # Otherwise markers don't appear 🤷
			close_on_submit=True,
			).add_to(m)
	MapSwapControl(
			maps={
					"🏴󠁧󠁢󠁥󠁮󠁧󠁿🏴󠁧󠁢󠁷󠁬󠁳󠁿 England & Wales": "https://domdfcoding.github.io/nhle-map/",
					'<i class="fa-solid fa-map fa-fw"></i> More': "https://domdfcoding.github.io/maps/",
					},
			).add_to(m)

	layer_control = add_to(LayerControl(), m, "basemap")
	OverlayState(layer_control).add_to(m)
	# BasemapState(osm_tiles.tile_name, layer_control).add_to(m)

	return m

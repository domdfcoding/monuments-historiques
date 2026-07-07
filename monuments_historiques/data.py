#!/usr/bin/env python3
#
#  data.py
"""
Data preparation.
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

# stdlib
import datetime
import json
from typing import Any
from urllib.parse import urljoin

# 3rd party
import requests
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike

__all__ = ["download_data"]


def download_data(output_directory: PathLike) -> dict[str, Any]:
	"""
	Download data from ``data.gouv.fr``.

	:param output_directory: Directory to write files to.
	"""

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make(parents=True)

	base_url = "https://tabular-api.data.gouv.fr"
	rid = "3a52af4a-f9da-4dcc-8110-b07774dfb3bc"

	meta_url = urljoin(base_url, f"/api/resources/{rid}/")
	profile_url = urljoin(base_url, f"/api/resources/{rid}/profile/")
	data_url = urljoin(base_url, f"/api/resources/{rid}/data/json/")

	meta_resp = requests.get(meta_url)
	meta_resp.raise_for_status()
	meta_json = meta_resp.json()

	created_at = datetime.datetime.fromisoformat(meta_json["created_at"]).astimezone(datetime.timezone.utc)

	profile_resp = requests.get(profile_url)
	profile_resp.raise_for_status()
	profile_json = profile_resp.json()

	total_lines = profile_json["profile"]["total_lines"]

	description_en = "This map presents buildings and buildings that have been or are protected under Historic Monuments (classified or inscribed), from the year 1840 to the present. The list presents all the information available on the Mérimée base, which itself comes from the order and the protection file, drawn up by the Historic Monuments service. Protected buildings date from prehistory in the 20th century."
	description_fr = "Cette carte présente les édifices et immeubles qui ont été ou sont protégés au titre des Monuments historiques (classés ou inscrits), depuis l’année 1840 jusqu’à aujourd’hui. La liste présente l’ensemble des informations disponibles sur la base Mérimée, qui proviennent elles-mêmes de l’arrêté et du dossier de protection, établis par le service des Monuments historiques. Les édifices protégés datent de la Préhistoire au 20e siècle."

	layers = [{
			"name": "Monuments Historiques",
			"description": description_en,
			"description-fr": description_fr,
			"serviceItemId": profile_json["dataset_id"],
			"copyrightText": '',  # TODO
			"editingInfo": {
					"dataLastEditDate": created_at.timestamp(),
					"lastEditDate": created_at.timestamp(),
					},
			}]
	meta: dict[str, Any] = {
			"start_time": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
			"layers": layers,
			}

	# TODO: check last edit date against meta.json to see if update needed

	data_resp = requests.get(data_url)
	data_resp.raise_for_status()
	data_json = data_resp.json()

	geojson = {
			"type": "FeatureCollection",
			"features": [],
			"totalFeatures": total_lines,
			"numberMatched": total_lines,
			"numberReturned": total_lines,
			"timeStamp": created_at.isoformat(),
			"crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
			}

	for feature in data_json:

		coords = feature.pop("coordonnees_au_format_WGS84")

		if not coords:
			continue

		lat, lng = json.loads(f"[{coords}]")

		entry_id = feature.pop("Reference")
		feature_properties = {"ListEntry": entry_id}
		geojson["features"].append({
				"type": "Feature",
				"id": entry_id,
				"geometry": {"type": "MultiPoint", "coordinates": [[lng, lat]]},
				"geometry_name": "geom",
				"properties": feature_properties,
				})

		for key, value in feature.items():
			if not value:
				continue

			# if key == "Destination_actuelle_de_l_edifice":  # Current use
			# 	feature_properties[""] = value
			# if key == "Adresse_forme_index":  # Address format?
			# 	feature_properties[""] = value
			# if key == "Etablissement_affectataire_de_l_edifice":  # Institution to which the building is assigned?
			# 	feature_properties[""] = value
			# if key == "Autre_appellation_de_l_edifice":  # Alternative name
			# 	feature_properties[""] = value
			if key == "Nature_de_la_protection":
				feature_properties["Grade"] = value
			# if key == "Auteur_de_l_edifice":  # Architect
			# 	feature_properties[""] = value
			# if key == "Cadastre":
			# 	feature_properties[""] = value
			# if key == "Commune_forme_index":  # Municipality standard form index
			# 	feature_properties[""] = value
			# if key == "Copyright":
			# 	feature_properties[""] = value
			# if key == "Type_de_couverture":  # Cover type?
			# 	feature_properties[""] = value
			if key == "Datation_de_l_edifice":  # Era
				feature_properties["Period"] = value
			if key == "Denomination_de_l_edifice":
				feature_properties["Name"] = value
			# if key == "Lieu_de_conservation_d_un_element_architectural_deplace":  # Location where a relocated architectural element is preserved
			# 	feature_properties[""] = value
			if key == "Description_de_l_edifice":
				feature_properties["Description"] = value  # TODO: add to notes?
			# if key == "Dimensions_normalisees_des_edicules_uniquement":  # Standardized dimensions?
			# 	feature_properties[""] = value
			# if key == "Date_de_Label":  # Label Date?
			# 	feature_properties[""] = value
			# if key == "Date_de_la_derniere_mise_a_jour":  # Last updated
			# 	feature_properties[""] = value
			if key == "Date_de_creation_de_la_notice":
				feature_properties["ListDate"] = datetime.datetime.fromisoformat(value).timestamp()
			# if key == "Domaine":  # Domain?
			# 	feature_properties[""] = value
			# if key == "Typologie_du_dossier":  # Case Type?
			# 	feature_properties[""] = value
			# if key == "Date_et_typologie_de_la_protection":  # Date and type of protection
			# 	feature_properties[""] = value
			# if key == "Departement_format_numerique":
			# 	feature_properties[""] = value
			# if key == "Departement_en_lettres":
			# 	feature_properties[""] = value
			# if key == "Partie_d_elevation_exterieure":  # Exterior elevation section
			# 	feature_properties[""] = value
			# if key == "Source_de_l_energie_utilisee_par_l_edifice":  # Source of energy
			# 	feature_properties[""] = value
			# if key == "Emplacement__forme_et_structure_de_l_escalier":  # Location, shape, and structure of the staircase
			# 	feature_properties[""] = value
			# if key == "Description_de_l_elevation_interieure":  # Description of the interior elevation
			# 	feature_properties[""] = value  # TODO: add to notes?
			# if key == "etat_de_conservation":  # Conservation status
			# 	feature_properties[""] = value
			# if key == "Cadre_de_l_etude":  # Study framework?
			# 	feature_properties[""] = value
			# if key == "Genre_du_destinataire":
			# 	feature_properties[""] = value
			# if key == "Historique":
			# 	feature_properties[""] = value
			# if key == "Nom_du_cours_d_eau_traversant_ou_bordant_l_edifice":  # Watercourse?
			# 	feature_properties[""] = value
			# if key == "Identifiant_Agregee":  # Aggregated Identifier
			# 	feature_properties[""] = value
			# if key == "COG_Insee_lors_de_la_protection":  # Something at time of protection?
			# 	feature_properties[""] = value
			# if key == "Justification_attribution":  # Justification (for listing)
			# 	feature_properties[""] = value
			# if key == "Justification_de_la_datation":  # Justification for dating (era)
			# 	feature_properties[""] = value
			# if key == "Liens_externes":  # External links  # TODO
			# 	feature_properties[""] = value
			# if key == "Lieudit":  # Locality
			# 	feature_properties[""] = value
			if key in {
					"Lien_vers_la_base_Archiv_MH",  #
					# "Lien_vers_la_base_Joconde",
					# "Lien_vers_la_base_Palissy",
					}:
				feature_properties["hyperlink"] = value
			# if key == "Materiaux_du_gros_oeuvre":  # Structural materials
			# 	feature_properties[""] = value
			# if key == "Nom_du_redacteur":  # Author Name?
			# 	feature_properties[""] = value
			if key == "Observations":
				feature_properties["Observations"] = value  # TODO: add to notes?
			# if key == "Precision_affectataire":
			# 	feature_properties[""] = value
			# if key == "Partie_constituante_non_etudiee":  # Unstudied constituent part?
			# 	feature_properties[""] = value
			# if key == "Partie_constituante":  # Constituent part
			# 	feature_properties[""] = value
			# if key == "Precision_sur_la_denomination":  # Clarification regarding the name
			# 	feature_properties[""] = value
			# if key == "Personnes_liees_a_l_edifice":  # People associated with the building
			# 	feature_properties[""] = value
			# if key == "Typologie_de_plan":  # Plan typology
			# 	feature_properties[""] = value
			# if key == "Precision_de_la_localisation":  # Location accuracy
			# 	feature_properties[""] = value
			# if key == "Precision_de_la_protection":  # Protection precision?
			# 	feature_properties[""] = value
			# if key == "Description_de_l_iconographie":  # Description of the iconography
			# 	feature_properties[""] = value
			# if key == "Typologie_de_la_protection":  # Typology of protection?
			# 	feature_properties[""] = value
			# if key == "Precision_sur_le_statut_de_l_edifice":  # Clarification regarding the status of the building
			# 	feature_properties[""] = value
			# if key == "Reference_a_un_ensemble":  # Reference to a set?
			# 	feature_properties[""] = value
			# if key == "References_des_parties_constituantes_etudiees":  # References of the constituent parts studied
			# 	feature_properties[""] = value
			# if key == "Region":
			# 	feature_properties[""] = value
			# if key == "Elements_remarquables_dans_l_edifice":  # Notable features of the building
			# 	feature_properties[""] = value
			# if key == "Remploi":  # Reuse
			# 	feature_properties[""] = value
			# if key == "Renvoi_vers_une_notice_de_la_base_Merimee_ou_Palissy":
			# 	feature_properties[""] = value
			# if key == "Indexation_iconographique_normalisee":  # Standardized iconographic indexing
			# 	feature_properties[""] = value
			# if key == "Siecle_de_campagne_secondaire_de_construction":  # Century of the secondary construction phase
			# 	feature_properties[""] = value
			# if key == "Siecle_de_la_campagne_principale_de_construction":  # Century of the main construction phase
			# 	feature_properties[""] = value
			# if key == "Format_abrege_du_siecle_de_construction":  # Abbreviated format of the century of construction
			# 	feature_properties[""] = value
			# if key == "Typologie_de_la_zone_de_protection":  # Typology of the protection zone
			# 	feature_properties[""] = value
			# if key == "Statut_juridique_de_l_edifice":  # Legal status of the building
			# 	feature_properties[""] = value
			# if key == "Technique_du_decor_porte_de_l_edifice":  # Decoration technique of the building's doorway
			# 	feature_properties[""] = value
			if key == "Titre_editorial_de_la_notice":
				feature_properties["Name"] = value  # TODO: translate into english
			# if key == "Materiaux_de_la_couverture":  # Roof material
			# 	feature_properties[""] = value
			# if key == "Couverts_ou_decouverts_du_jardin_de_l_edifice":  # Covered or uncovered areas of the building's garden
			# 	feature_properties[""] = value
			# if key == "Vocable___pour_les_edifices_cultuels":  # Dedication of places of worship? Faith maybe?
			# 	feature_properties[""] = value
			# if key == "Typologie_du_couvrement":  # Typology of roofing systems
			# 	feature_properties[""] = value
			# if key == "Adresse_forme_editoriale":
			# 	feature_properties[""] = value
			# if key == "Commune_forme_editoriale":
			# 	feature_properties[""] = value
			# if key == "Producteur:
			# 	feature_properties[""] = value

	(output_dir / "Monuments Historiques.geojson").dump_json(geojson)

	output_dir.joinpath("meta.json").dump_json(meta, indent=2)
	return meta

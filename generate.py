#!/usr/bin/env python3
"""
Generate the contacts-per-country dashboard.

Reads the CSV from sources/, normalizes country name variants,
aggregates duplicates, and injects the data as JSON into index.html.

Usage:
    python generate.py
    python generate.py --csv "sources/Counts per country - countries_all.csv"
"""

from __future__ import annotations

import csv
import json
import re
import argparse
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent

# ── Normalization: map every variant (lowercase) → canonical English name ──

NORMALIZE = {
    # Main countries (lowercase → canonical)
    "united states": "United States",
    "india": "India",
    "brazil": "Brazil",
    "brasil": "Brazil",
    "brazilië": "Brazil",
    "brazilia": "Brazil",
    "brazil metropolitan area": "Brazil",
    "united kingdom": "United Kingdom",
    "france": "France",
    "francia": "France",
    "frankrig": "France",
    "frankrike": "France",
    "frankrijk": "France",
    "canada": "Canada",
    "mexico": "Mexico",
    "méxico": "Mexico",
    "mexiko": "Mexico",
    "indonesia": "Indonesia",
    "italy": "Italy",
    "italia": "Italy",
    "italien": "Italy",
    "spain": "Spain",
    "españa": "Spain",
    "spain area": "Spain",
    "australia": "Australia",
    "germany": "Germany",
    "deutschland": "Germany",
    "alemania": "Germany",
    "tyskland": "Germany",
    "colombia": "Colombia",
    "turkey": "Turkey",
    "türkiye": "Turkey",
    "argentina": "Argentina",
    "china": "China",
    "中国": "China",
    "中华人民共和国": "China",
    "philippines": "Philippines",
    "pilipinas": "Philippines",
    "filipinas": "Philippines",
    "philipines": "Philippines",
    "netherlands": "Netherlands",
    "nederland": "Netherlands",
    "south africa": "South Africa",
    "south africa metropolitan area": "South Africa",
    "iriphabliki yaseningizimu afrika": "South Africa",
    "pakistan": "Pakistan",
    "پاکستان": "Pakistan",
    "peru": "Peru",
    "perú": "Peru",
    "chile": "Chile",
    "egypt": "Egypt",
    "مصر": "Egypt",
    "united arab emirates": "United Arab Emirates",
    "saudi arabia": "Saudi Arabia",
    "السعودية": "Saudi Arabia",
    "malaysia": "Malaysia",
    "nigeria": "Nigeria",
    "russia": "Russia",
    "россия": "Russia",
    "poland": "Poland",
    "polska": "Poland",
    "polen": "Poland",
    "polonia": "Poland",
    "polaand": "Poland",
    "sweden": "Sweden",
    "sverige": "Sweden",
    "vietnam": "Vietnam",
    "belgium": "Belgium",
    "belgië": "Belgium",
    "portugal": "Portugal",
    "portugalia": "Portugal",
    "portugalsko": "Portugal",
    "bangladesh": "Bangladesh",
    "বাংলাদেশ": "Bangladesh",
    "ecuador": "Ecuador",
    "switzerland": "Switzerland",
    "schweiz": "Switzerland",
    "venezuela": "Venezuela",
    "iran": "Iran",
    "ایران": "Iran",
    "singapore": "Singapore",
    "morocco": "Morocco",
    "المغرب": "Morocco",
    "romania": "Romania",
    "românia": "Romania",
    "denmark": "Denmark",
    "danmark": "Denmark",
    "dänemark": "Denmark",
    "kenya": "Kenya",
    "ukraine": "Ukraine",
    "україна": "Ukraine",
    "украина": "Ukraine",
    "thailand": "Thailand",
    "ประเทศไทย": "Thailand",
    "japan": "Japan",
    "日本": "Japan",
    "اليابان": "Japan",
    "ireland": "Ireland",
    "new zealand": "New Zealand",
    "south korea": "South Korea",
    "algeria": "Algeria",
    "الجزائر": "Algeria",
    "algérie": "Algeria",
    "norway": "Norway",
    "norge": "Norway",
    "taiwan": "Taiwan",
    "台湾": "Taiwan",
    "hong kong s.a.r.": "Hong Kong",
    "hong kong sar": "Hong Kong",
    "israel": "Israel",
    "czechia": "Czechia",
    "česko": "Czechia",
    "austria": "Austria",
    "österreich": "Austria",
    "áustria": "Austria",
    "greece": "Greece",
    "ελλάδα": "Greece",
    "ghana": "Ghana",
    "sri lanka": "Sri Lanka",
    "ශ්‍රී ලංකාව": "Sri Lanka",
    "dominican republic": "Dominican Republic",
    "república dominicana": "Dominican Republic",
    "finland": "Finland",
    "suomi": "Finland",
    "finlandia": "Finland",
    "finlandiya": "Finland",
    "tunisia": "Tunisia",
    "تونس": "Tunisia",
    "guatemala": "Guatemala",
    "bolivia": "Bolivia",
    "costa rica": "Costa Rica",
    "hungary": "Hungary",
    "uruguay": "Uruguay",
    "jordan": "Jordan",
    "jordania": "Jordan",
    "qatar": "Qatar",
    "serbia": "Serbia",
    "србија": "Serbia",
    "nepal": "Nepal",
    "iraq": "Iraq",
    "iraque": "Iraq",
    "panama": "Panama",
    "puerto rico": "Puerto Rico",
    "bulgaria": "Bulgaria",
    "българия": "Bulgaria",
    "lebanon": "Lebanon",
    "tanzania": "Tanzania",
    "el salvador": "El Salvador",
    "senegal": "Senegal",
    "sénégal": "Senegal",
    "uganda": "Uganda",
    "paraguay": "Paraguay",
    "kuwait": "Kuwait",
    "kuwait city metropolitan area": "Kuwait",
    "croatia": "Croatia",
    "hrvatska": "Croatia",
    "cameroon": "Cameroon",
    "cameroun": "Cameroon",
    "honduras": "Honduras",
    "oman": "Oman",
    "عمان": "Oman",
    "kazakhstan": "Kazakhstan",
    "казахстан": "Kazakhstan",
    "slovakia": "Slovakia",
    "slovensko": "Slovakia",
    "ethiopia": "Ethiopia",
    "ኢትዮጵያ": "Ethiopia",
    "angola": "Angola",
    "jamaica": "Jamaica",
    "zimbabwe": "Zimbabwe",
    "myanmar": "Myanmar",
    "nicaragua": "Nicaragua",
    "côte d\u2019ivoire": "Ivory Coast",
    "côte d'ivoire": "Ivory Coast",
    "ivory coast": "Ivory Coast",
    "lithuania": "Lithuania",
    "lietuva": "Lithuania",
    "zambia": "Zambia",
    "azerbaijan": "Azerbaijan",
    "azerbaycan": "Azerbaijan",
    "belarus": "Belarus",
    "беларусь": "Belarus",
    "республика беларусь": "Belarus",
    "trinidad and tobago": "Trinidad and Tobago",
    "bahrain": "Bahrain",
    "georgia": "Georgia",
    "mozambique": "Mozambique",
    "slovenia": "Slovenia",
    "slovenija": "Slovenia",
    "斯洛文尼亚": "Slovenia",
    "cambodia": "Cambodia",
    "cyprus": "Cyprus",
    "κύπρος": "Cyprus",
    "albania": "Albania",
    "shqipëria": "Albania",
    "latvia": "Latvia",
    "letonia": "Latvia",
    "syria": "Syria",
    "mauritius": "Mauritius",
    "sudan": "Sudan",
    "democratic republic of congo": "DR Congo",
    "democratic republic of the congo": "DR Congo",
    "congo (drc": "DR Congo",
    "luxembourg": "Luxembourg",
    "afghanistan": "Afghanistan",
    "bosnia and herzegovina": "Bosnia and Herzegovina",
    "bosna i hercegovina": "Bosnia and Herzegovina",
    "botswana": "Botswana",
    "papua new guinea": "Papua New Guinea",
    "estonia": "Estonia",
    "eesti": "Estonia",
    "armenia": "Armenia",
    "армения": "Armenia",
    "namibia": "Namibia",
    "malta": "Malta",
    "cuba": "Cuba",
    "palestine": "Palestine",
    "فلسطين": "Palestine",
    "palestinian state": "Palestine",
    "gaza strip": "Palestine",
    "west bank": "Palestine",
    "libya": "Libya",
    "ليبيا": "Libya",
    "uzbekistan": "Uzbekistan",
    "узбекистан": "Uzbekistan",
    "oʻzbekiston": "Uzbekistan",
    "rwanda": "Rwanda",
    "benin": "Benin",
    "mali": "Mali",
    "burkina faso": "Burkina Faso",
    "moldova": "Moldova",
    "republica moldova": "Moldova",
    "yemen": "Yemen",
    "اليمن": "Yemen",
    "madagascar": "Madagascar",
    "haiti": "Haiti",
    "ayiti": "Haiti",
    "iceland": "Iceland",
    "ísland": "Iceland",
    "malawi": "Malawi",
    "guinea": "Guinea",
    "guinée": "Guinea",
    "mongolia": "Mongolia",
    "togo": "Togo",
    "fiji": "Fiji",
    "the bahamas": "Bahamas",
    "somalia": "Somalia",
    "gabon": "Gabon",
    "barbados": "Barbados",
    "maldives": "Maldives",
    "congo": "Congo",
    "republic of the congo": "Congo",
    "liberia": "Liberia",
    "guyana": "Guyana",
    "sierra leone": "Sierra Leone",
    "kyrgyzstan": "Kyrgyzstan",
    "montenegro": "Montenegro",
    "црна гора": "Montenegro",
    "brunei": "Brunei",
    "brunei darussalam": "Brunei",
    "north macedonia": "North Macedonia",
    "kosovo": "Kosovo",
    "eswatini": "Eswatini",
    "the gambia": "Gambia",
    "suriname": "Suriname",
    "mauritania": "Mauritania",
    "bhutan": "Bhutan",
    "laos": "Laos",
    "belize": "Belize",
    "lesotho": "Lesotho",
    "curacao": "Curaçao",
    "new caledonia": "New Caledonia",
    "guam": "Guam",
    "cape verde": "Cape Verde",
    "chad": "Chad",
    "tchad": "Chad",
    "cayman islands": "Cayman Islands",
    "french polynesia": "French Polynesia",
    "bermuda": "Bermuda",
    "burundi": "Burundi",
    "reunion": "Réunion",
    "aruba": "Aruba",
    "andorra": "Andorra",
    "south sudan": "South Sudan",
    "st. lucia": "Saint Lucia",
    "saint lucia": "Saint Lucia",
    "djibouti": "Djibouti",
    "monaco": "Monaco",
    "isle of man": "Isle of Man",
    "virgin islands, u.s.": "U.S. Virgin Islands",
    "us virgin islands": "U.S. Virgin Islands",
    "tajikistan": "Tajikistan",
    "niger": "Niger",
    "antigua and barbuda": "Antigua and Barbuda",
    "grenada": "Grenada",
    "guernsey": "Guernsey",
    "seychelles": "Seychelles",
    "turkmenistan": "Turkmenistan",
    "gibraltar": "Gibraltar",
    "central african republic": "Central African Republic",
    "east timor": "East Timor",
    "timor-leste": "East Timor",
    "equatorial guinea": "Equatorial Guinea",
    "american samoa": "American Samoa",
    "jersey": "Jersey",
    "french guiana": "French Guiana",
    "dominica": "Dominica",
    "liechtenstein": "Liechtenstein",
    "st vincent and the grenadines": "Saint Vincent and the Grenadines",
    "saint vincent and the grenadines": "Saint Vincent and the Grenadines",
    "turks and caicos islands": "Turks and Caicos Islands",
    "greenland": "Greenland",
    "solomon islands": "Solomon Islands",
    "saint kitts and nevis": "Saint Kitts and Nevis",
    "st kitts and nevis": "Saint Kitts and Nevis",
    "british virgin islands": "British Virgin Islands",
    "virgin islands, british": "British Virgin Islands",
    "faroe islands": "Faroe Islands",
    "vanuatu": "Vanuatu",
    "french-guadeloupe": "Guadeloupe",
    "guadeloupe": "Guadeloupe",
    "comoros": "Comoros",
    "northern mariana islands": "Northern Mariana Islands",
    "guinea-bissau": "Guinea-Bissau",
    "anguilla": "Anguilla",
    "samoa": "Samoa",
    "san marino": "San Marino",
    "tonga": "Tonga",
    "antarctica": "Antarctica",
    "federated states of micronesia": "Micronesia",
    "eritrea": "Eritrea",
    "eretria": "Eritrea",
    "sao tome and principe": "São Tomé and Príncipe",
    "são tomé and príncipe": "São Tomé and Príncipe",
    "french-martinique": "Martinique",
    "martinique": "Martinique",
    "sint maarten": "Sint Maarten",
    "kiribati": "Kiribati",
    "cook islands": "Cook Islands",
    "palau": "Palau",
    "mayotte": "Mayotte",
    "vatican": "Vatican City",
    "vatican city": "Vatican City",
    "bonaire": "Bonaire",
    "macau s.a.r.": "Macau",
    "macao sar": "Macau",
    "north korea": "North Korea",
    "falkland islands (malvinas)": "Falkland Islands",
    "falkland islands": "Falkland Islands",
    "tuvalu": "Tuvalu",
    "saint pierre and miquelon": "Saint Pierre and Miquelon",
    "wallis and futuna": "Wallis and Futuna",
    "christmas island": "Christmas Island",
    "montserrat": "Montserrat",
    "nauru": "Nauru",
    "saint helena": "Saint Helena",
    "niue": "Niue",
    "french southern territories": "French Southern Territories",
    "saint barthelemy": "Saint Barthélemy",
    "st martin": "Saint Martin",
    "norfolk island": "Norfolk Island",
    "marshall islands": "Marshall Islands",
    "western sahara": "Western Sahara",
}

# ISO-3 codes
COUNTRY_ISO = {
    "United States": "USA", "India": "IND", "Brazil": "BRA",
    "United Kingdom": "GBR", "France": "FRA", "Canada": "CAN",
    "Mexico": "MEX", "Indonesia": "IDN", "Italy": "ITA",
    "Spain": "ESP", "Australia": "AUS", "Germany": "DEU",
    "Colombia": "COL", "Turkey": "TUR", "Argentina": "ARG",
    "China": "CHN", "Philippines": "PHL", "Netherlands": "NLD",
    "South Africa": "ZAF", "Pakistan": "PAK", "Peru": "PER",
    "Chile": "CHL", "Egypt": "EGY", "United Arab Emirates": "ARE",
    "Saudi Arabia": "SAU", "Malaysia": "MYS", "Nigeria": "NGA",
    "Russia": "RUS", "Poland": "POL", "Sweden": "SWE",
    "Vietnam": "VNM", "Belgium": "BEL", "Portugal": "PRT",
    "Bangladesh": "BGD", "Ecuador": "ECU", "Switzerland": "CHE",
    "Venezuela": "VEN", "Iran": "IRN", "Singapore": "SGP",
    "Morocco": "MAR", "Romania": "ROU", "Denmark": "DNK",
    "Kenya": "KEN", "Ukraine": "UKR", "Thailand": "THA",
    "Japan": "JPN", "Ireland": "IRL", "New Zealand": "NZL",
    "South Korea": "KOR", "Algeria": "DZA", "Norway": "NOR",
    "Taiwan": "TWN", "Hong Kong": "HKG", "Israel": "ISR",
    "Czechia": "CZE", "Austria": "AUT", "Finland": "FIN",
    "Greece": "GRC", "Hungary": "HUN", "Croatia": "HRV",
    "Bulgaria": "BGR", "Serbia": "SRB", "Slovakia": "SVK",
    "Slovenia": "SVN", "Lithuania": "LTU", "Latvia": "LVA",
    "Estonia": "EST", "Luxembourg": "LUX", "Iceland": "ISL",
    "Costa Rica": "CRI", "Panama": "PAN", "Uruguay": "URY",
    "Dominican Republic": "DOM", "Guatemala": "GTM",
    "Bolivia": "BOL", "Paraguay": "PRY", "Honduras": "HND",
    "El Salvador": "SLV", "Nicaragua": "NIC", "Cuba": "CUB",
    "Jamaica": "JAM", "Trinidad and Tobago": "TTO",
    "Puerto Rico": "PRI", "Ghana": "GHA", "Tanzania": "TZA",
    "Ethiopia": "ETH", "Uganda": "UGA", "Mozambique": "MOZ",
    "Cameroon": "CMR", "Tunisia": "TUN", "Libya": "LBY",
    "Senegal": "SEN", "Zimbabwe": "ZWE", "Zambia": "ZMB",
    "Rwanda": "RWA", "Angola": "AGO", "Jordan": "JOR",
    "Lebanon": "LBN", "Iraq": "IRQ", "Kuwait": "KWT",
    "Oman": "OMN", "Qatar": "QAT", "Bahrain": "BHR",
    "Sri Lanka": "LKA", "Myanmar": "MMR", "Cambodia": "KHM",
    "Nepal": "NPL", "Mongolia": "MNG", "Georgia": "GEO",
    "Azerbaijan": "AZE", "Belarus": "BLR", "Ivory Coast": "CIV",
    "Cyprus": "CYP", "Albania": "ALB", "Syria": "SYR",
    "Mauritius": "MUS", "Sudan": "SDN", "DR Congo": "COD",
    "Afghanistan": "AFG", "Bosnia and Herzegovina": "BIH",
    "Botswana": "BWA", "Papua New Guinea": "PNG",
    "Armenia": "ARM", "Namibia": "NAM", "Malta": "MLT",
    "Palestine": "PSE", "Uzbekistan": "UZB", "Benin": "BEN",
    "Mali": "MLI", "Burkina Faso": "BFA", "Moldova": "MDA",
    "Yemen": "YEM", "Madagascar": "MDG", "Haiti": "HTI",
    "Malawi": "MWI", "Guinea": "GIN", "Togo": "TGO",
    "Fiji": "FJI", "Bahamas": "BHS", "Somalia": "SOM",
    "Gabon": "GAB", "Barbados": "BRB", "Maldives": "MDV",
    "Congo": "COG", "Liberia": "LBR", "Guyana": "GUY",
    "Sierra Leone": "SLE", "Kyrgyzstan": "KGZ",
    "Montenegro": "MNE", "Brunei": "BRN",
    "North Macedonia": "MKD", "Kosovo": "XKX",
    "Eswatini": "SWZ", "Gambia": "GMB", "Suriname": "SUR",
    "Mauritania": "MRT", "Bhutan": "BTN", "Laos": "LAO",
    "Belize": "BLZ", "Lesotho": "LSO", "Curaçao": "CUW",
    "New Caledonia": "NCL", "Guam": "GUM", "Cape Verde": "CPV",
    "Chad": "TCD", "Cayman Islands": "CYM",
    "French Polynesia": "PYF", "Bermuda": "BMU",
    "Burundi": "BDI", "Réunion": "REU", "Aruba": "ABW",
    "Andorra": "AND", "South Sudan": "SSD",
    "Saint Lucia": "LCA", "Djibouti": "DJI", "Monaco": "MCO",
    "Isle of Man": "IMN", "U.S. Virgin Islands": "VIR",
    "Tajikistan": "TJK", "Niger": "NER",
    "Antigua and Barbuda": "ATG", "Grenada": "GRD",
    "Guernsey": "GGY", "Seychelles": "SYC",
    "Turkmenistan": "TKM", "Gibraltar": "GIB",
    "Central African Republic": "CAF", "East Timor": "TLS",
    "Equatorial Guinea": "GNQ", "American Samoa": "ASM",
    "Jersey": "JEY", "French Guiana": "GUF",
    "Dominica": "DMA", "Liechtenstein": "LIE",
    "Saint Vincent and the Grenadines": "VCT",
    "Turks and Caicos Islands": "TCA", "Greenland": "GRL",
    "Solomon Islands": "SLB", "Saint Kitts and Nevis": "KNA",
    "British Virgin Islands": "VGB", "Faroe Islands": "FRO",
    "Vanuatu": "VUT", "Guadeloupe": "GLP", "Comoros": "COM",
    "Northern Mariana Islands": "MNP", "Guinea-Bissau": "GNB",
    "Anguilla": "AIA", "Samoa": "WSM", "San Marino": "SMR",
    "Tonga": "TON", "Antarctica": "ATA", "Micronesia": "FSM",
    "Eritrea": "ERI", "São Tomé and Príncipe": "STP",
    "Martinique": "MTQ", "Sint Maarten": "SXM",
    "Kiribati": "KIR", "Cook Islands": "COK", "Palau": "PLW",
    "Mayotte": "MYT", "Vatican City": "VAT", "Bonaire": "BES",
    "Macau": "MAC", "North Korea": "PRK",
    "Falkland Islands": "FLK", "Tuvalu": "TUV",
    "Saint Pierre and Miquelon": "SPM",
    "Wallis and Futuna": "WLF", "Christmas Island": "CXR",
    "Montserrat": "MSR", "Nauru": "NRU",
    "Saint Helena": "SHN", "Niue": "NIU",
    "French Southern Territories": "ATF",
    "Saint Barthélemy": "BLM", "Saint Martin": "MAF",
    "Norfolk Island": "NFK", "Marshall Islands": "MHL",
    "Western Sahara": "ESH", "Kazakhstan": "KAZ",
}

# Region mapping by ISO code
REGION_MAP = {
    "USA": "North America", "CAN": "North America", "PRI": "North America",
    "BMU": "North America", "GRL": "North America",
    "GBR": "Europe", "FRA": "Europe", "DEU": "Europe", "ITA": "Europe",
    "ESP": "Europe", "NLD": "Europe", "BEL": "Europe", "CHE": "Europe",
    "AUT": "Europe", "PRT": "Europe", "SWE": "Europe", "NOR": "Europe",
    "DNK": "Europe", "FIN": "Europe", "IRL": "Europe", "POL": "Europe",
    "ROU": "Europe", "CZE": "Europe", "HUN": "Europe", "GRC": "Europe",
    "BGR": "Europe", "HRV": "Europe", "SRB": "Europe", "SVK": "Europe",
    "SVN": "Europe", "LTU": "Europe", "LVA": "Europe", "EST": "Europe",
    "LUX": "Europe", "ISL": "Europe", "TUR": "Europe", "UKR": "Europe",
    "RUS": "Europe", "BLR": "Europe", "MDA": "Europe", "ALB": "Europe",
    "MNE": "Europe", "MKD": "Europe", "BIH": "Europe", "XKX": "Europe",
    "CYP": "Europe", "MLT": "Europe", "GEO": "Europe", "AZE": "Europe",
    "ARM": "Europe", "AND": "Europe", "MCO": "Europe", "LIE": "Europe",
    "SMR": "Europe", "VAT": "Europe", "GIB": "Europe", "IMN": "Europe",
    "GGY": "Europe", "JEY": "Europe", "FRO": "Europe",
    "BRA": "Latam", "MEX": "Latam", "ARG": "Latam", "COL": "Latam",
    "CHL": "Latam", "PER": "Latam", "ECU": "Latam", "VEN": "Latam",
    "CRI": "Latam", "PAN": "Latam", "URY": "Latam", "DOM": "Latam",
    "GTM": "Latam", "BOL": "Latam", "PRY": "Latam", "HND": "Latam",
    "SLV": "Latam", "NIC": "Latam", "CUB": "Latam", "JAM": "Latam",
    "TTO": "Latam", "HTI": "Latam", "BRB": "Latam", "GUY": "Latam",
    "SUR": "Latam", "BLZ": "Latam", "BHS": "Latam", "DMA": "Latam",
    "GRD": "Latam", "LCA": "Latam", "VCT": "Latam", "KNA": "Latam",
    "ATG": "Latam", "TCA": "Latam", "CYM": "Latam", "ABW": "Latam",
    "CUW": "Latam", "SXM": "Latam", "VIR": "Latam", "VGB": "Latam",
    "AIA": "Latam", "MSR": "Latam", "GUF": "Latam", "GLP": "Latam",
    "MTQ": "Latam", "BES": "Latam", "MAF": "Latam", "BLM": "Latam",
    "SPM": "Latam", "FLK": "Latam",
    "IND": "Asia-Pacific", "CHN": "Asia-Pacific", "JPN": "Asia-Pacific",
    "KOR": "Asia-Pacific", "AUS": "Asia-Pacific", "NZL": "Asia-Pacific",
    "IDN": "Asia-Pacific", "PHL": "Asia-Pacific", "THA": "Asia-Pacific",
    "VNM": "Asia-Pacific", "MYS": "Asia-Pacific", "SGP": "Asia-Pacific",
    "TWN": "Asia-Pacific", "HKG": "Asia-Pacific", "PAK": "Asia-Pacific",
    "BGD": "Asia-Pacific", "LKA": "Asia-Pacific", "MMR": "Asia-Pacific",
    "KHM": "Asia-Pacific", "NPL": "Asia-Pacific", "MNG": "Asia-Pacific",
    "LAO": "Asia-Pacific", "BTN": "Asia-Pacific", "MDV": "Asia-Pacific",
    "BRN": "Asia-Pacific", "PNG": "Asia-Pacific", "FJI": "Asia-Pacific",
    "WSM": "Asia-Pacific", "TON": "Asia-Pacific", "VUT": "Asia-Pacific",
    "SLB": "Asia-Pacific", "FSM": "Asia-Pacific", "PLW": "Asia-Pacific",
    "MHL": "Asia-Pacific", "KIR": "Asia-Pacific", "TUV": "Asia-Pacific",
    "COK": "Asia-Pacific", "NIU": "Asia-Pacific", "TLS": "Asia-Pacific",
    "NCL": "Asia-Pacific", "PYF": "Asia-Pacific", "GUM": "Asia-Pacific",
    "ASM": "Asia-Pacific", "MNP": "Asia-Pacific", "NFK": "Asia-Pacific",
    "CXR": "Asia-Pacific", "MAC": "Asia-Pacific", "PRK": "Asia-Pacific",
    "AFG": "Asia-Pacific", "KAZ": "Asia-Pacific", "KGZ": "Asia-Pacific",
    "TJK": "Asia-Pacific", "UZB": "Asia-Pacific", "TKM": "Asia-Pacific",
    "WLF": "Asia-Pacific", "REU": "Asia-Pacific", "MYT": "Asia-Pacific",
    "ZAF": "Middle East & Africa", "NGA": "Middle East & Africa",
    "EGY": "Middle East & Africa", "KEN": "Middle East & Africa",
    "GHA": "Middle East & Africa", "TZA": "Middle East & Africa",
    "ETH": "Middle East & Africa", "UGA": "Middle East & Africa",
    "MOZ": "Middle East & Africa", "CMR": "Middle East & Africa",
    "TUN": "Middle East & Africa", "LBY": "Middle East & Africa",
    "SEN": "Middle East & Africa", "ZWE": "Middle East & Africa",
    "ZMB": "Middle East & Africa", "RWA": "Middle East & Africa",
    "AGO": "Middle East & Africa", "DZA": "Middle East & Africa",
    "MAR": "Middle East & Africa",
    "ARE": "Middle East & Africa", "SAU": "Middle East & Africa",
    "ISR": "Middle East & Africa", "IRN": "Middle East & Africa",
    "JOR": "Middle East & Africa", "LBN": "Middle East & Africa",
    "IRQ": "Middle East & Africa", "KWT": "Middle East & Africa",
    "OMN": "Middle East & Africa", "QAT": "Middle East & Africa",
    "BHR": "Middle East & Africa", "SYR": "Middle East & Africa",
    "PSE": "Middle East & Africa", "YEM": "Middle East & Africa",
    "SDN": "Middle East & Africa", "SSD": "Middle East & Africa",
    "SOM": "Middle East & Africa", "DJI": "Middle East & Africa",
    "ERI": "Middle East & Africa", "MUS": "Middle East & Africa",
    "MRT": "Middle East & Africa", "MLI": "Middle East & Africa",
    "BFA": "Middle East & Africa", "NER": "Middle East & Africa",
    "TCD": "Middle East & Africa", "CAF": "Middle East & Africa",
    "COD": "Middle East & Africa", "COG": "Middle East & Africa",
    "GAB": "Middle East & Africa", "GNQ": "Middle East & Africa",
    "BEN": "Middle East & Africa", "TGO": "Middle East & Africa",
    "CIV": "Middle East & Africa", "BDI": "Middle East & Africa",
    "MWI": "Middle East & Africa", "MDG": "Middle East & Africa",
    "GIN": "Middle East & Africa", "GNB": "Middle East & Africa",
    "LBR": "Middle East & Africa", "SLE": "Middle East & Africa",
    "GMB": "Middle East & Africa", "CPV": "Middle East & Africa",
    "SWZ": "Middle East & Africa", "LSO": "Middle East & Africa",
    "BWA": "Middle East & Africa", "NAM": "Middle East & Africa",
    "SYC": "Middle East & Africa", "COM": "Middle East & Africa",
    "STP": "Middle East & Africa", "SHN": "Middle East & Africa",
    "ESH": "Middle East & Africa",
}

# Rows to skip entirely (metropolitan areas, regions, junk)
SKIP_PATTERNS = [
    "metropolitan area", "region", "district", "dach", "apac", "namer",
    "area", "loralai", "jafarabad", "panjgur", "ziarat", "mastung",
    "hazara town", "shikarpur", "zhob", "kingman reef", "palmyra atoll",
    "wake island", "howland island", "shikotan island", "pa-li-chia-ssu",
    "svalbard", "jan mayen", "tokelau", "pitcairn", "heard island",
    "united states minor outlying islands", "south georgia and the south sandwich islands",
    "south georgia and south sandwich islands", "british indian ocean territory",
    "french southern and antarctic lands", "åland islands",
    "golan heights", "golan heights subdistrict",
    "sint eustatius and saba", "saint eustatius", "ascension and tristan da cunha",
    "republikken kina",
]


def should_skip(name: str) -> bool:
    """Check if a row should be skipped."""
    low = name.lower().strip()
    # Skip if it's purely a metro area reference and already counted in parent
    for pat in SKIP_PATTERNS:
        if low == pat or (pat in low and low not in NORMALIZE):
            # Only skip if not in our normalize table
            if low not in NORMALIZE:
                return True
    return False


def normalize_country(name: str) -> str | None:
    """Return canonical country name, or None to skip."""
    low = name.lower().strip()
    if should_skip(low):
        return None
    canonical = NORMALIZE.get(low)
    if canonical:
        return canonical
    # Try title case lookup in COUNTRY_ISO
    title = name.strip().title()
    if title in COUNTRY_ISO:
        return title
    return None


def load_csv(path: Path) -> list[dict]:
    """Load CSV, normalize, and aggregate by country."""
    aggregated: dict[str, int] = defaultdict(int)
    skipped = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_name = row.get("country", "").strip()
            if not raw_name:
                continue

            # Parse count
            contacts = 0
            for col in ["contacts", "count", "total", "nb_contacts", "total_contacts"]:
                if col in row and row[col]:
                    contacts = int(str(row[col]).replace(",", "").replace(" ", "").strip())
                    break

            canonical = normalize_country(raw_name)
            if canonical:
                aggregated[canonical] += contacts
            else:
                skipped.append((raw_name, contacts))

    if skipped:
        # Only show skipped with significant counts
        big_skips = [(n, c) for n, c in skipped if c >= 100]
        if big_skips:
            print(f"\n  Skipped {len(skipped)} rows ({len(big_skips)} with 100+ contacts):")
            for n, c in sorted(big_skips, key=lambda x: -x[1])[:20]:
                print(f"    - {n}: {c:,}")
        else:
            print(f"  Skipped {len(skipped)} rows (all < 100 contacts)")

    # Build final data list
    data = []
    for country, contacts in aggregated.items():
        iso = COUNTRY_ISO.get(country)
        if not iso:
            print(f"  Warning: no ISO code for '{country}', skipping")
            continue
        region = REGION_MAP.get(iso, "Other")
        data.append({
            "country": country,
            "iso": iso,
            "region": region,
            "contacts": contacts,
        })

    return data


def inject_data(data: list[dict]) -> None:
    """Replace DATA = [...] in index.html with actual data."""
    html_path = ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")

    json_str = json.dumps(data, ensure_ascii=False)
    html = re.sub(
        r"const DATA = \[.*?\];",
        f"const DATA = {json_str};",
        html,
        count=1,
        flags=re.DOTALL,
    )
    html_path.write_text(html, encoding="utf-8")
    print(f"  Injected {len(data)} countries into index.html")


def main():
    parser = argparse.ArgumentParser(description="Generate contacts-per-country map")
    parser.add_argument(
        "--csv",
        default="sources/Counts per country - countries_all.csv",
        help="Path to CSV file",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = ROOT / csv_path

    if not csv_path.exists():
        print(f"Error: CSV not found at {csv_path}")
        return

    print(f"Loading data from {csv_path.name}")
    data = load_csv(csv_path)
    data.sort(key=lambda d: d["contacts"], reverse=True)

    total = sum(d["contacts"] for d in data)
    regions = defaultdict(int)
    for d in data:
        regions[d["region"]] += d["contacts"]

    print(f"\n  {len(data)} countries, {total:,} total contacts")
    print(f"  By region:")
    for r, c in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"    {r}: {c:,} ({c/total*100:.1f}%)")

    inject_data(data)
    print("\nDone! Open index.html in a browser to preview.")


if __name__ == "__main__":
    main()

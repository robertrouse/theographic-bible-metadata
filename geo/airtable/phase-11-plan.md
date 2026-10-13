# Phase 11 Plan: Airtable `places`

Snapshot before any change: `json/places.json` at commit `bc4c1f1` (tag `airtable-places-backup-2026-10-13`); no record was modified after that export.

## 1. New field

`canonicalPlace`: link to another `places` record, single. Set only on alias records.

## 2. Set canonicalPlace on 251 alias records (180 canonical places)

| Alias record | → Canonical record | Feature |
|---|---|---|
| #352 Ebron | #3 Abdon | Abdon |
| #4 Abel | #5 Abel-beth-maacah | Abel-Beth-Maacah |
| #7 Abel-maim | #5 Abel-beth-maacah | Abel-Beth-Maacah |
| #221 Beth-maacah | #5 Abel-beth-maacah | Abel-Beth-Maacah |
| #959 Ptolemais | #15 Acco | Accho |
| #291 Chezib | #18 Achzib | Achzib (of Judah) |
| #309 Cozeba | #18 Achzib | Achzib (of Judah) |
| #755 Mahalab | #35 Ahlab | Ahlab |
| #38 Aiath | #36 Ai | Ai of Joshua |
| #39 Aija | #36 Ai | Ai of Joshua |
| #45 Alemeth | #49 Almon | Almon |
| #75 Aphik | #71 Aphek | Aphek (of Asher) |
| #70 Antipatris | #72 Aphek | Aphek of Sharon |
| #74 Aphekah | #72 Aphek | Aphek of Sharon |
| #260 Arabah | #79 Arabah | Arabah |
| #1225 River of Arnon | #92 Arnon | Arnon |
| #1014 Rumah | #98 Arumah | Arumah |
| #132 Azotus | #101 Ashdod | Ashdod |
| #171 Beeshterah | #106 Ashtaroth | Ashtaroth |
| #670 Karnaim | #107 Ashteroth-karnaim | Ashteroth-Karnaim |
| #109 Asshur | #111 Assyria | Assyria |
| #898 Nimrod | #111 Assyria | Assyria |
| #9 Abel-mizraim | #112 Atad | Atad |
| #605 Ivvah | #123 Avva | Avva |
| #192 Beth-azmaveth | #129 Azmaveth | Azmaveth (town) |
| #176 Beon | #144 Baal-meon | Baal-meon |
| #193 Beth-baal-meon | #144 Baal-meon | Baal-meon |
| #223 Beth-meon | #144 Baal-meon | Baal-meon |
| #133 Baal | #138 Baalath-beer | Baalath-beer |
| #161 Bealoth | #138 Baalath-beer | Baalath-beer |
| #162 Bealoth | #138 Baalath-beer | Baalath-beer |
| #982 Ramoth | #138 Baalath-beer | Baalath-beer |
| #150 Babel | #151 Babylon | Babel |
| #781 Merathaim | #151 Babylon | Babel |
| #928 Pekod | #151 Babylon | Babel |
| #153 Baharum | #154 Bahurim | Bahurim |
| #165 Beer | #164 Beer | Beer |
| #1075 Shibah | #170 Beersheba | Beer-Sheba |
| #169 Beeroth Bene-jaakan | #174 Bene-jaakan | Bene-jaakan |
| #437 Benjamin's Gate | #175 Gate of Benjamin | Benjamin Gate |
| #180 Berothai | #179 Berothah | Berothah |
| #311 Cun | #179 Berothah | Berothah |
| #212 Beth-haran | #211 Beth-haram | Beth-Haram |
| #987 Rehob | #230 Beth-rehob | Beth-Rehob |
| #233 Beth-shean | #232 Beth-shan | Beth-Shan |
| #733 Beth-horon | #214 Beth-horon | Beth-horon |
| #896 Nimrah | #225 Beth-nimrah | Beth-nimrah |
| #600 Ir-shemesh | #234 Beth-shemesh | Beth-shemesh (of Judah) |
| #194 Beth-barah | #187 Bethany | Bethany (Beyond the Jordan) |
| #121 Aven | #202 Bethel (of Palestine) | Bethel (North of Jerusalem) |
| #191 Beth-aven | #202 Bethel (of Palestine) | Bethel (North of Jerusalem) |
| #252 Bochim | #202 Bethel (of Palestine) | Bethel (North of Jerusalem) |
| #367 El-bethel | #202 Bethel (of Palestine) | Bethel (North of Jerusalem) |
| #737 Luz | #202 Bethel (of Palestine) | Bethel (North of Jerusalem) |
| #220 Bethlehem Ephrathah | #218 Bethlehem | Bethlehem (of Judah) |
| #403 Ephrath | #218 Bethlehem | Bethlehem (of Judah) |
| #257 Bozrah | #256 Bozrah | Bozrah (in Edom) |
| #270 Calno | #269 Calneh | Calneh |
| #667 Kanah | #271 Cana | Cana |
| #297 Chisloth-tabor | #290 Chesulloth | Chesulloth |
| #294 Chinnereth | #293 Chinnereth | Chinnereth |
| #295 Chinneroth | #293 Chinnereth | Chinnereth |
| #557 Heliopolis | #908 On | City of the Sun |
| #275 Caphtor | #310 Crete | Crete |
| #419 Ethiopia | #312 Cush | Cush (region) |
| #315 Cuthah | #314 Cuth | Cuth |
| #370 Elishah | #316 Cyprus | Cyprus |
| #707 Kittim | #316 Cyprus | Cyprus |
| #713 Laish | #323 Dan | Dan (city) |
| #727 Leshem | #323 Dan | Dan (city) |
| #702 Kiriath-sannah | #325 Debir | Debir (of South Hill Country) |
| #703 Kiriath-sepher | #325 Debir | Debir (of South Hill Country) |
| #333 Dibon-gad | #331 Dibon | Dibon (north of the Arnon River) |
| #875 Naphath-dor | #341 Dor | Dor |
| #877 Naphoth-dor | #341 Dor | Dor |
| #958 East Gate | #349 East Gate | East Gate |
| #408 Esau | #357 Edom | Edom |
| #969 Rahab | #362 Egypt | Egypt (nation) |
| #366 Elath | #375 Eloth | Eloth |
| #377 Elteke | #378 Eltekeh | Eltekeh |
| #1174 Tolad | #380 Eltolad | Eltolad |
| #64 Anem | #388 En-gannim | En-gannim (of Issachar) |
| #542 Hazazon-tamar | #389 Engedi | Engedi |
| #923 Pas-dammim | #399 Ephes-dammim | Ephes-dammim |
| #438 Gate of Ephraim | #402 Gate of Ephraim | Ephraim Gate |
| #413 Eshtemoh | #412 Eshtemoa | Eshtemoa |
| #1010 River | #421 Euphrates | Euphrates |
| #791 Metheg-ammah | #442 Gath | Gath |
| #448 Geba | #447 Geba | Geba |
| #453 Gederoth | #452 Gederah | Geder |
| #454 Gederothaim | #452 Gederah | Geder |
| #451 Geder | #455 Gedor | Gedor (of Judah) |
| #456 Gedor | #455 Gedor | Gedor (of Judah) |
| #1203 Valley of Gerar | #459 Gerar | Gerar |
| #483 Gob | #463 Gezer | Gezer |
| #1204 Valley of Gibeon | #470 Gibeon | Gibeon |
| #208 Beth-gilgal | #476 Gilgal | Gilgal (near Jericho) |
| #457 Geliloth | #476 Gilgal | Gilgal (near Jericho) |
| #478 Gilo | #479 Giloh | Giloh |
| #954 Place | #487 Golgotha | Golgotha |
| #1153 Place | #487 Golgotha | Golgotha |
| #1154 Skull | #487 Golgotha | Golgotha |
| #517 Hamath-zobah | #516 Hamath | Hamath-Zobah |
| #723 Lebo-hamath | #516 Hamath | Hamath-Zobah |
| #519 Hammon | #518 Hammath | Hammath (Place) |
| #520 Hammoth-dor | #518 Hammath | Hammath (Place) |
| #619 Jair | #535 Havvoth-jair | Havvoth-jair |
| #541 Hazar-susim | #540 Hazar-susah | Hazar-Susah |
| #697 Kiriath-arba | #551 Hebron | Hebron (city) |
| #840 Mount Heres | #562 Heres | Heres |
| #570 Hilen | #572 Holon | Hilon |
| #496 Gudgodah | #579 Hor-haggidgad | Hor-Haggidgad |
| #584 Forest | #585 Lebanon | House of the Forest of Lebanon |
| #587 Hukok | #586 Hukkok | Hukkok |
| #248 Bileam | #589 Ibleam | Ibleam |
| #445 Gath-rimmon | #589 Ibleam | Ibleam |
| #641 Jetur | #604 Ituraea | Ituraea |
| #607 Iyim | #606 Iye-abarim | Iye-abarim |
| #610 Jabesh | #611 Jabesh-gilead | Jabesh-Gilead |
| #615 Jabneh | #613 Jabneel | Jabneel (of Judah) |
| #618 Jahzah | #617 Jahaz | Jahaz |
| #495 Greece | #627 Javan | Javan (region) |
| #89 Ariel | #636 Jerusalem | Jerusalem |
| #303 City of the Lord | #636 Jerusalem | Jerusalem |
| #629 Jebus | #636 Jerusalem | Jerusalem |
| #1018 Salem | #636 Jerusalem | Jerusalem |
| #651 Joktheel | #650 Joktheel | Joktheel |
| #658 Judea | #657 Judea | Judea |
| #633 Jekabzeel | #660 Kabzeel | Kabzeel |
| #393 En-mishpat | #663 Kadesh-barnea | Kadesh-barnea |
| #661 Kadesh | #663 Kadesh-barnea | Kadesh-barnea |
| #677 Kedesh | #663 Kadesh-barnea | Kadesh-barnea |
| #696 Kiriathaim | #672 Kartan | Kartan |
| #679 Kedesh-naphtali | #676 Kedesh | Kedesh |
| #901 Nobah | #682 Kenath | Kenath |
| #905 Nophah | #682 Kenath | Kenath |
| #547 Hazor | #684 Kerioth-hezron | Kerioth-hezron |
| #648 Jokmeam | #686 Kibzaim | Kibzaim |
| #688 Brook Kidron | #687 Kidron | Kidron |
| #814 Mizpeh | #693 Kir | Kir |
| #135 Baalah | #701 Kiriath-jearim | Kiriath-jearim |
| #139 Baale-judah | #701 Kiriath-jearim | Kiriath-jearim |
| #608 Jaar | #701 Kiriath-jearim | Kiriath-jearim |
| #698 Kiriath-arim | #701 Kiriath-jearim | Kiriath-jearim |
| #699 Kiriath-baal | #701 Kiriath-jearim | Kiriath-jearim |
| #678 Kedesh | #704 Kishion | Kishion |
| #671 Kartah | #706 Kitron | Kitron |
| #673 Kattath | #706 Kitron | Kitron |
| #327 Debir | #732 Lo-debar | Lo-debar |
| #741 Lydda | #731 Lod | Lod |
| #83 Aram-maacah | #743 Maacah | Maacah (kingdom) |
| #744 Maacath | #743 Maacah | Maacah (kingdom) |
| #222 Beth-marcaboth | #749 Madmannah | Madmannah (town) |
| #320 Dalmanutha | #753 Magadan | Magadan |
| #1011 Rock | #764 Maon | Maon |
| #91 Armageddon | #777 Megiddo | Megiddo |
| #784 Meribah-kadesh | #782 Meribah (of Kadesh) | Meribah (at Kadesh) |
| #789 Meshech-Tubal | #788 Meshech | Meshech (region) |
| #84 Aram-naharaim | #790 Mesopotamia | Mesopotamia |
| #792 Michmas | #793 Michmash | Michmash |
| #769 Mashal | #805 Mishal | Mishal |
| #90 Arimathea | #811 Mizpah | Mizpah |
| #812 Mizpeh | #811 Mizpah | Mizpah |
| #975 Ramah | #811 Mizpah | Mizpah |
| #977 Ramathaim-zophim | #811 Mizpah | Mizpah |
| #432 Galeed | #809 Mizpah | Mizpah of Gilead |
| #631 Jegar-sahadutha | #809 Mizpah | Mizpah of Gilead |
| #979 Ramath-mizpeh | #809 Mizpah | Mizpah of Gilead |
| #820 Moresheth-gath | #819 Moresheth | Moresheth |
| #823 Moserah | #824 Moseroth | Moseroth |
| #405 Ephron | #834 Mount Ephron | Mount Ephron |
| #406 Ephron | #834 Mount Ephron | Mount Ephron |
| #564 Hermon | #841 Mount Hermon | Mount Hermon |
| #829 Mount Baalhermon | #841 Mount Hermon | Mount Hermon |
| #856 Mount Sion | #841 Mount Hermon | Mount Hermon |
| #1047 Senir | #841 Mount Hermon | Mount Hermon |
| #1101 Sirion | #841 Mount Hermon | Mount Hermon |
| #821 Moriah | #848 Mount Moriah | Mount Moriah |
| #145 Baal-peor | #933 Peor | Mount Peor |
| #1042 Seir | #852 Mount Seir | Mount Seir (of Edom) |
| #576 Horeb | #855 Mount Sinai | Mount Sinai |
| #844 Mount Horeb | #855 Mount Sinai | Mount Sinai |
| #1098 Sinai | #855 Mount Sinai | Mount Sinai |
| #1237 Zalmon | #858 Mount Zalmon | Mount Zalmon |
| #1263 Zion | #860 Mount Zion | Mount Zion |
| #828 Mount of Olives | #861 Mount of Olives | Mount of Olives |
| #907 Olivet | #861 Mount of Olives | Mount of Olives |
| #867 Naarah | #868 Naaran | Naaran |
| #871 Nahalol | #869 Nahalal | Nahalal |
| #1110 South | #885 Negeb | Negeb |
| #524 Hapharaim | #914 Ophrah | Ophrah (of Manasseh) |
| #915 Paddan | #916 Paddan-aram | Paddan-Aram |
| #917 Pai | #927 Pau | Pau |
| #930 Peniel | #931 Penuel | Penuel (city) |
| #934 Perez-uzza | #935 Perez-uzzah | Perez-Uzzah |
| #1036 Sea of the Philistines | #943 Philistia | Philistia |
| #506 Hahiroth | #948 Pi-hahiroth | Pi-Hahiroth |
| #735 Lud | #962 Put | Put (nation) |
| #960 Pul | #962 Put | Put (nation) |
| #58 Ammon | #966 Rabbah | Rabbah (Ammon) |
| #514 Ham | #966 Rabbah | Rabbah (Ammon) |
| #965 Raamses | #980 Rameses | Rameses |
| #994 Remeth | #981 Ramoth | Ramoth |
| #976 Ramah | #984 Ramoth-gilead | Ramoth-gilead |
| #983 Ramoth | #984 Ramoth-gilead | Ramoth-gilead |
| #394 En-rimmon | #1004 Rimmon | Rimmon (of Judah) |
| #335 Dimnah | #1005 Rimmon | Rimmon (of Zebulun) |
| #1006 Rimmono | #1005 Rimmon | Rimmon (of Zebulun) |
| #1035 Sea of the Plain | #1021 Salt Sea | Salt Sea |
| #1029 Sea of Chinnereth | #1032 Sea of Galilee | Sea of Galilee |
| #1030 Sea of Chinneroth | #1032 Sea of Galilee | Sea of Galilee |
| #1034 Sea of Tiberias | #1032 Sea of Galilee | Sea of Galilee |
| #1052 Shaalabbin | #1053 Shaalbim | Shaalbim |
| #1056 Shaaraim | #1055 Shaaraim | Shaaraim |
| #1079 Shilhim | #1065 Sharuhen | Sharuhen |
| #1178 Shechem (tower) | #1069 Shechem | Shechem (city) |
| #1083 Shimron-meron | #1082 Shimron | Shimron (city) |
| #10 Abel-shittim | #1086 Shittim | Shittim |
| #1038 Sebam | #1091 Sibmah | Sibmah |
| #494 Sidon | #1093 Sidon | Sidon (city) |
| #1094 Sidon | #1093 Sidon | Sidon (city) |
| #691 Pool | #1096 Siloam | Siloam |
| #957 Pool | #1096 Siloam | Siloam |
| #1080 Shiloah | #1096 Siloam | Siloam |
| #1104 Soco | #1105 Socoh | Socoh (in the Shephelah) |
| #65 Aner | #1124 Taanach | Taanach |
| #857 Mount Tabor | #1128 Tabor (Mountain) | Tabor (Mountain) |
| #1134 Tamar | #1131 Tadmor | Tadmor |
| #1141 Tehaphnehes | #1133 Tahpanhes | Tahpanhes |
| #1144 Telaim | #1146 Telem | Telem (village) |
| #430 Gabbatha | #1155 Pavement | The Stone Pavement |
| #970 Rakkath | #1161 Tiberias | Tiberias |
| #182 Betah | #1162 Tibhath | Tibhath |
| #1167 Timnath-serah | #1166 Timnath-heres | Timnath-Heres |
| #734 Beth-horon | #1188 Upper Beth-horon | Upper Beth-Horon |
| #1227 Valley of the Passengers | #1205 Valley of Hamongog | Valley of Hamon-gog |
| #1176 Topheth | #1207 Valley of Hinnom | Valley of Hinnom |
| #1199 Valley of Baca | #1207 Valley of Hinnom | Valley of Hinnom |
| #1219 Valley of Slaughter | #1207 Valley of Hinnom | Valley of Hinnom |
| #1226 Valley of the Son of Hinnom | #1207 Valley of Hinnom | Valley of Hinnom |
| #810 Mizpah | #1213 Valley of Mizpeh | Valley of Mizpeh |
| #995 Rephaim | #1214 Valley of Rephaim | Valley of Rephaim |
| #1262 Zin | #1261 Zin | Wilderness of Zin |
| #1256 Zererah | #1243 Zarethan | Zarethan |
| #1251 Zephath | #580 Hormah | Zephath |
| #1224 Valley of Zered | #1253 Zered | Zered |
| #1255 Zeredah | #1254 Zeredah | Zeredah |
| #172 Bela | #1271 Zoar | Zoar |
| #1236 Zair | #1271 Zoar | Zoar |
| #85 Aram-zobah | #1272 Zobah | Zobah |
| #1273 Zobah-Hamath | #1272 Zobah | Zobah |

## 3. Create 24 records

| placeID | placeLookup | displayTitle | featureType | coordinates | verses | from |
|---|---|---|---|---|---|---|
| 1279 | el-elohe-israel_1279 | El-elohe-Israel | Landmark | 35.281944, 32.213611 | 1 | places-0390 |
| 1280 | judah_1280 | Judah | Region | ,  | 27 | places-0611 |
| 1281 | israel-united_1281 | Israel (United) | Region | 35.234167, 31.776667 | 0 | places-1255 |
| 1282 | israel-northern-kingdom_1282 | Israel (Northern Kingdom) | Region | 35.195, 32.276111 | 0 | places-1256 |
| 1283 | judah-southern_1283 | Judah (Southern) | Region | 35.234167, 31.776667 | 8 | places-1257 |
| 1284 | reuben_1284 | Reuben | Region | 35.809062, 31.800811 | 12 | places-1258 |
| 1285 | dan_1285 | Dan | Region | 34.985289, 31.773992 | 9 | places-1259 |
| 1286 | naphtali_1286 | Naphtali | Region | 35.569167, 33.018333 | 16 | places-1260 |
| 1287 | edrei_1287 | Edrei | City | ,  | 1 | places-1261 |
| 1288 | gad_1288 | Gad | Region | 35.745805, 32.046967 | 21 | places-1262 |
| 1289 | asher_1289 | Asher | Region | 35.158133, 32.914536 | 20 | places-1264 |
| 1290 | issachar_1290 | Issachar | Region | 35.42031, 32.648544 | 13 | places-1265 |
| 1291 | zebulun_1291 | Zebulun | Region | 35.239568, 32.714861 | 16 | places-1266 |
| 1292 | east-manasseh-half-tribe_1292 | East Manasseh (Half-Tribe) | Region | 36.071543, 32.641108 | 14 | places-1268 |
| 1293 | west-manasseh_1293 | West Manasseh | Region | 35.310064, 32.481922 | 19 | places-1269 |
| 1294 | ephraim-territory_1294 | Ephraim (Territory) | Region | 35.232834, 32.016322 | 15 | places-1270 |
| 1295 | benjamin-territory_1295 | Benjamin (Territory) | Region | 35.263257, 31.853294 | 14 | places-1271 |
| 1296 | forest-of-ephraim_1296 | Forest of Ephraim | Region | 35.764722, 32.381111 | 2 | places-1273 |
| 1297 | misgab_1297 | Misgab | City | 35.701389, 31.180556 | 1 | places-1274 |
| 1298 | parbar_1298 | Parbar | Landmark | 35.234167, 31.776667 | 1 | places-1275 |
| 1299 | sela-hammahlekoth_1299 | Rock of Escape | Mountain | 35.232889, 31.451513 | 2 | places-1276 |
| 1300 | caleb-ephratah_1300 | Caleb-Ephrathah | City | 35.207639, 31.704306 | 1 | places-1277 |
| 1301 | machbenah_1301 | Machbenah | City | 34.896797, 31.554151 | 1 | places-1281 |
| 1302 | jorkoam_1302 | Jorkeam | City | 35.118489, 31.461967 | 1 | places-1283 |

## Not changed

- No existing field value is overwritten and no record is deleted.
- Records excluded from the LPF file (possessives, "There", Azazel, people groups, Temple rooms) stay as they are.
- Coordinates, names and verse links of existing records are not touched.

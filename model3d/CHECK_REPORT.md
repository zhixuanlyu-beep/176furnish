# 模型检查报告

文件完整性：**passed**；Blender 5.2.1 LTS。

Blend 对象 779；材质 11；重新导入 GLB 网格 654。

几何及使用问题按下表保留；文件通过不等于通道、开启空间及施工条件全部通过。

| 检查 | 结果 |
|---|---|
| blender_background | True |
| metres | True |
| seven_cameras | True |
| room_collections | True |
| materials | True |
| lights | True |
| configuration_matches | True |
| hidden_candidates | True |
| six_seat_alternative_hidden | True |
| C_north_no_leaf | True |
| C_west_2200 | True |
| CD_wall_preserved | True |
| A_window_south | True |
| kitchen_closable | True |
| bedA_mattress | True |
| bedB_mattress | True |
| bedD_mattress | True |
| coffee_dimensions | True |
| sofa_dimensions | True |
| desk_dimensions | True |
| table4_dimensions | True |
| table6_dimensions | True |
| all_mesh_dimensions_positive | True |
| glb_import | True |
| glb_mesh_count | True |
| glb_no_candidate_mesh | True |
| glb_no_six_seat_mesh | True |

## 通道估算

| 状态 | 北侧就座 mm | 北侧拉椅 mm | 南椅至咖啡柜 mm | 南椅至烤箱全开 mm |
|---|---:|---:|---:|---:|
| 4人 | 20 | -330 | 548 | -2 |
| 6人 | 20 | -330 | 548 | -2 |

## 未解决碰撞与条件

| 类别 | 对象 | 详情 | 处理 |
|---|---|---|---|
| service_chair | chair4_2, coffee_operator | {"seats": 4, "pulled": false, "overlap_mm": [275.0, 450.0, 800.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair4_2, oven_open | {"seats": 4, "pulled": false, "overlap_mm": [225.0, 2.0, 350.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair4_3, coffee_operator | {"seats": 4, "pulled": false, "overlap_mm": [500.0, 450.0, 800.0]} | South row must vacate before opening/servicing equipment. |
| pulled_chair_wall | chair4_0, kitchen_south_glass_glass | {"seats": 4, "pulled": true, "overlap_mm": [500.0, 40.0, 765.0]} | Full pull-out obstructed; adjust seating use or furniture position. |
| pulled_chair_wall | chair4_1, kitchen_south_glass_glass | {"seats": 4, "pulled": true, "overlap_mm": [500.0, 40.0, 765.0]} | Full pull-out obstructed; adjust seating use or furniture position. |
| service_chair | chair4_2, coffee_drawer | {"seats": 4, "pulled": true, "overlap_mm": [275.0, 302.0, 550.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair4_2, coffee_operator | {"seats": 4, "pulled": true, "overlap_mm": [275.0, 498.0, 800.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair4_2, oven_open | {"seats": 4, "pulled": true, "overlap_mm": [225.0, 352.0, 350.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair4_3, coffee_drawer | {"seats": 4, "pulled": true, "overlap_mm": [500.0, 302.0, 550.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair4_3, coffee_operator | {"seats": 4, "pulled": true, "overlap_mm": [500.0, 498.0, 800.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair6_3, oven_open | {"seats": 6, "pulled": false, "overlap_mm": [500.0, 2.0, 350.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair6_4, coffee_operator | {"seats": 6, "pulled": false, "overlap_mm": [500.0, 450.0, 800.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair6_5, coffee_operator | {"seats": 6, "pulled": false, "overlap_mm": [500.0, 450.0, 800.0]} | South row must vacate before opening/servicing equipment. |
| pulled_chair_wall | chair6_0, kitchen_south_glass_glass | {"seats": 6, "pulled": true, "overlap_mm": [500.0, 40.0, 765.0]} | Full pull-out obstructed; adjust seating use or furniture position. |
| pulled_chair_wall | chair6_1, kitchen_south_glass_glass | {"seats": 6, "pulled": true, "overlap_mm": [500.0, 40.0, 765.0]} | Full pull-out obstructed; adjust seating use or furniture position. |
| pulled_chair_wall | chair6_2, kitchen_south_glass_glass | {"seats": 6, "pulled": true, "overlap_mm": [500.0, 40.0, 765.0]} | Full pull-out obstructed; adjust seating use or furniture position. |
| service_chair | chair6_3, oven_open | {"seats": 6, "pulled": true, "overlap_mm": [500.0, 352.0, 350.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair6_4, coffee_drawer | {"seats": 6, "pulled": true, "overlap_mm": [500.0, 302.0, 550.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair6_4, coffee_operator | {"seats": 6, "pulled": true, "overlap_mm": [500.0, 498.0, 800.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair6_5, coffee_drawer | {"seats": 6, "pulled": true, "overlap_mm": [500.0, 302.0, 550.0]} | South row must vacate before opening/servicing equipment. |
| service_chair | chair6_5, coffee_operator | {"seats": 6, "pulled": true, "overlap_mm": [500.0, 498.0, 800.0]} | South row must vacate before opening/servicing equipment. |
| passage | Dining_4, north_route | {"north_route_seated_mm": 20, "north_route_pulled_mm": -330, "south_chair_to_coffee_mm": 548, "south_chair_to_open_oven_mm": -2} | Closed glass prevents full north chair pull-out. Dining seating needs further layout review; access from west, no north passage asserted. |
| passage | Dining_6, north_route | {"north_route_seated_mm": 20, "north_route_pulled_mm": -330, "south_chair_to_coffee_mm": 548, "south_chair_to_open_oven_mm": -2} | Closed glass prevents full north chair pull-out. Dining seating needs further layout review; access from west, no north passage asserted. |
| unconfirmed_structural | headers, wall_thickness | "Image cannot resolve original beams, columns or load-bearing classification." | Site survey required; no construction clearance asserted. |
| conditional_equipment | island_sink, laundry, robot | "No hidden pipework; island gravity drain and balcony sanitary connection unverified." | Confirm connection levels and equipment models before installation. |
| bathroom_assumptions | Bath_A, Bath_Public | "Sanitary fixtures modeled as assumed concept positions, not inferred confirmed plumbing." | Survey fixture footprints and wet-zone boundaries. |

## 尺寸假设

- Existing R10 exterior footprints retain 240mm where already defined; 220mm is the fallback for new thick walls. No structural boundary is trimmed.
- Door widths are concept clear openings before detailed frames; positions and hinge sides estimated.
- C west opening narrowed to 2200mm by retaining a south pier; header is conceptual, structural design pending.
- Kitchen south fixed glazing restores enclosure along removed partition M01; west 1000mm sliding door closes connection. Former C north 900mm portal has no leaf.
- Dining table moved 350mm south and deepened 50mm to clear kitchen glass; island remains fixed; table-island overlap along edge is now 425mm.
- Coffee enlarged from 1300 to 1700mm in place; pantry reduced from 901 to 501mm, equipment order unchanged.
- Study east glass face at X=-480mm leaves a 1000mm route to A; desk shifted 170mm west and deep storage shortened to avoid its working space.
- Study glass partitions and all bathroom fixture placements are concept assumptions; existing plumbing positions are not confirmed.
- No hidden water, drain, gas or refrigerant routing is modeled. Island sink remains conditional: gravity drain not established.
- Beams over openings are placeholders; original structural columns cannot be independently identified from source image.

## 检查范围

- No local Cycles render; configured lights/materials/cameras verified by data.
- Door sweep sampled at 90 animation frames with conservative AABBs; hardware tolerances and exact continuous sweep not certified.
- Cabinet fronts are closed geometry with separate service envelopes; manufacturer hinges not modeled.
- Floorplan derived from dimension-anchored R10 wall faces, not independently surveyed coordinates.

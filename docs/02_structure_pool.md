# Structure Pool / 结构池

Version: v0.1

## Role

The structure pool is not the final user-facing output.

It is an internal hypothesis space used by ScenePack and AI models to understand how the user organized a visual scene.

中文：

结构池不是给用户看的标签堆，而是系统和大模型理解用户布局行为的路径约束。

## Design Principle

Internal pool wide, external output narrow.

中文：

内部候选池要宽，外部输出要窄。内部允许弱信号，外部必须有置信门槛。

## Layer 1: Spatial Metrics

These are observable facts.

- `box`
- `position`
- `size`
- `area_weight`
- `visible_area`
- `visible_weight`
- `overlap_field`
- `distance_field`
- `nearest_neighbor`
- `local_density`
- `whitespace_ratio`
- `screen_zone`
- `scale_tier`
- `containment`
- `edge_distance`

## Layer 2: Spatial Graphs

These build relations without full pairwise explosion.

- `knn_graph`
- `delaunay_graph`
- `mst_graph`
- `adjacency_graph`
- `community`
- `centrality`
- `bridge_node`
- `hub_node`
- `island_node`
- `boundary_node`

## Layer 3: Organization Forms

These describe visible structure.

- `cluster`
- `row`
- `column`
- `grid`
- `matrix`
- `band`
- `stack`
- `pile`
- `balanced_set`
- `quadrant`
- `center_periphery`
- `hub_spoke`
- `chain`
- `tree_like`
- `frame`
- `multi_zone`
- `dense_pool`
- `sparse_field`
- `outlier`

## Layer 4: Cognitive Practice Signals

These reflect common human layout behavior. They are candidates, not final semantic claims.

- `attention_anchor`
- `primary_candidate`
- `secondary_candidate`
- `peer_group_candidate`
- `comparison_frame_candidate`
- `process_path_candidate`
- `reference_pool_candidate`
- `evidence_group_candidate`
- `problem_zone_candidate`
- `solution_zone_candidate`
- `input_zone_candidate`
- `output_zone_candidate`
- `draft_zone_candidate`
- `pending_area_candidate`
- `confirmed_area_candidate`
- `temporary_storage_candidate`
- `background_material_candidate`
- `mainline_candidate`
- `side_branch_candidate`

## Layer 5: Information Compression

These decide how much detail should be preserved or collapsed.

- `representative_item`
- `region_summary`
- `compression_gain`
- `structure_entropy`
- `redundancy_group`
- `uncertain_group`
- `do_not_expand`
- `expand_on_demand`
- `low_detail_group`
- `high_value_group`

## Layer 6: Temporal Change

These describe how the scene changes over time.

- `new_item`
- `removed_item`
- `moved_item`
- `resized_item`
- `stable_anchor`
- `volatile_region`
- `layout_drift`
- `merged_group`
- `split_group`
- `snapshot_distance`
- `repeated_structure`
- `title_stability_signal`

## Layer 7: Inference Gates

These decide whether generation is allowed.

- `title_candidate_allowed`
- `title_confidence`
- `needs_title_confirmation`
- `user_acceptance_signal`
- `silent_generation_ready`
- `semantic_risk`
- `mixed_context_warning`
- `should_not_infer`
- `needs_image_reading`
- `needs_user_text`

## Example: Small Image

A small image is not automatically low value.

Possible structural interpretations:

- small and dense: collection element
- small and near a large item: supporting item
- small and isolated: boundary material or pending item
- small with large whitespace: isolated signal, not necessarily weak
- small and stable: placed material
- small and frequently moved: unresolved material

Required features:

- `size_weight`
- `local_density`
- `whitespace_ratio`
- `isolation_score`
- `nearest_group_distance`
- `attachment_score`
- `stability_score`
- `boundary_role`

## Quality Rule

ScenePack should never reduce structure to only `left_of`, `right_of`, `above`, and `below`.

The product value depends on converting layout behavior into a rich but controlled structural representation.


from settings import BOT_IMAGE_DIR, ARTIFACT_IMAGE_DIR


GAME_LOCATIONS = {
    "bottom_bar": {
        "bottom_master": (39, 781),
        "bottom_heroes": (120, 781),
        "bottom_equipment": (200, 781),
        "bottom_pets": (281, 781),
        "bottom_artifacts": (362, 781),
        "bottom_shop": (442, 781),
    },
    "daily_reward": {
        "rewards_open": (34, 176),
        "rewards_close": (430, 226),
        "rewards_collect": (240, 526),
    },
    "inbox": {
        "inbox_icon": (31, 361),
        "inbox_clan": (343, 106),
        "inbox_news": (142, 106),
    },
    "clan": {
        "clan_icon": (82, 25),
        "clan_info": (194, 728),
        "clan_info_header": (351, 82),
        "clan_info_close": (431, 34),
        "clan_previous_raid": (373, 298),
        "clan_results_copy": (83, 226),
        "clan_raid": (109, 716),
    },
    "skill_bar": {
        "bar_heavenly_strike": (43, 710),
        "bar_deadly_strike": (123, 710),
        "bar_hand_of_midas": (200, 710),
        "bar_fire_sword": (283, 710),
        "bar_war_cry": (363, 710),
        "bar_shadow_clone": (444, 710),
    },
    "game_screen": {
        "game_fight_boss": (425, 31),
        "game_middle": (250, 286),
        "game_player": (235, 387),
        "game_pet_gold": (287, 377),
        "game_pet_attack": (235, 343),
        "game_clan_ship": (60, 154),
        # Scrolling functions placed here, these represent different start and stop
        # points that our drag function can use to properly drag panels.
        "game_scroll_start": (328, 496),
        "game_scroll_top_end": (328, 731),
        "game_scroll_bottom_end": (328, 46),
        "game_scroll_quick_stop": (328, 746),
        # Fairies tapping map is looped through whenever the generic tapping process occurs.
        # It performs generic clicks from the top, towards the bottom of the screen, while
        # also clicking some additional locations to collect on screen items.
        "game_fairies_map": (
            (75, 91), (100, 91), (140, 91), (200, 91), (260, 91), (320, 91), (380, 91), (440, 91),
            (75, 126), (100, 126), (140, 126), (200, 126), (260, 126), (320, 126), (380, 126), (440, 126),
            (75, 196), (100, 196), (140, 196), (200, 196), (260, 196), (320, 196), (380, 196), (440, 196),
            (75, 266), (100, 266), (140, 266), (200, 266), (260, 266), (320, 266), (380, 266), (440, 266),
            (75, 336), (100, 336), (140, 336), (200, 336), (260, 336), (320, 336), (380, 336), (440, 336),
            (75, 406), (100, 406), (140, 406), (200, 406), (260, 406), (320, 406), (380, 406), (406, 406),
            # Click on pet for gold bonus if one is currently available
            # in game during tapping.
            (285, 366),
            # Click on spot where skill points appear to collect skill points
            # that may be available from stage progression.
            (110, 411),
            # Click on spot where equipment appears when enough stages
            # are surpassed, or when daily equipment is reset.
            (355, 411),
        ),
        "game_collect_clan_crate": (70, 131),
    },
    "minigames": {
        "minigame_coordinated_offensive": (
            (139, 403), (154, 403), (160, 405), (150, 404), (162, 404), (143, 402), (162, 401), (148, 409), (159, 401),
            (166, 406), (155, 389), (179, 411), (157, 404), (162, 400), (162, 403), (167, 407), (156, 404), (160, 404),
            (161, 404), (139, 403), (154, 403), (160, 405), (150, 404), (162, 404), (143, 402), (162, 401), (148, 409),
            (159, 401), (166, 406), (155, 389), (179, 411), (157, 404), (162, 400), (162, 403), (167, 407), (156, 404),
            (160, 404), (161, 404),
        ),
        "minigame_astral_awakening": (
            (449, 159), (413, 171), (403, 215), (458, 215), (455, 257), (395, 256), (405, 292), (454, 292), (451, 328),
            (396, 331), (374, 349), (453, 344), (452, 377), (393, 381), (399, 408), (445, 406), (450, 343), (408, 344),
            (387, 298), (440, 299), (472, 296), (463, 243), (412, 243), (381, 249), (381, 210), (449, 208), (466, 201),
            (439, 164), (396, 164), (449, 159), (413, 171), (403, 215), (458, 215), (455, 257), (395, 256), (405, 292),
            (454, 292), (451, 328), (396, 331), (374, 349), (453, 344), (452, 377), (393, 381), (399, 408), (445, 406),
            (450, 343), (408, 344), (387, 298), (440, 299), (472, 296), (463, 243), (412, 243), (381, 249), (381, 210),
            (449, 208), (466, 201), (439, 164), (396, 164), (1, 162), (1, 176), (1, 190), (1, 204), (1, 218), (1, 232),
            (1, 246), (1, 260), (1, 274), (1, 288), (1, 302), (1, 316), (1, 330), (1, 344), (1, 358), (1, 372),
            (1, 386), (1, 400), (1, 414), (1, 428), (1, 442),
        ),
        "minigame_heart_of_midas": (
            (299, 388), (291, 384), (293, 402), (299, 388), (291, 384), (293, 402),
        ),
        "minigame_flash_zip": (
            (172, 344), (141, 288), (112, 214), (124, 158), (233, 141), (305, 144), (369, 162), (381, 230), (336, 351),
            (333, 293), (283, 371), (213, 367), (155, 291), (159, 179), (254, 145), (327, 206), (320, 286), (273, 342),
            (216, 313), (224, 219), (172, 344), (141, 288), (112, 214), (124, 158), (233, 141), (305, 144), (369, 162),
            (381, 230), (336, 351), (333, 293), (283, 371), (213, 367), (155, 291), (159, 179), (254, 145), (327, 206),
            (320, 286), (273, 342), (216, 313), (224, 219),
        ),
        "minigame_forbidden_contract": (
            (205, 394), (172, 374), (156, 359), (143, 350), (114, 326), (105, 302), (105, 287), (116, 207), (118, 203),
            (125, 198), (144, 194), (166, 187), (199, 162), (234, 161), (275, 165), (308, 169), (321, 184), (198, 394),
            (165, 374), (152, 359), (139, 350), (110, 326), (100, 302), (101, 287), (111, 207), (114, 203), (119, 198),
            (139, 194), (160, 187), (194, 162), (230, 161), (270, 165), (300, 169), (315, 184), (209, 394), (176, 374),
            (162, 359), (150, 350), (119, 326), (111, 302), (108, 287), (120, 207), (125, 203), (127, 198), (149, 194),
            (171, 187), (204, 162), (239, 161), (280, 165), (314, 169), (325, 184),
        ),
    },
    "panel": {
        "panel_expand_or_collapse_top": (386, 9),
        "panel_expand_or_collapse_bottom": (386, 444),
        "panel_close_top": (449, 9),
        "panel_close_bottom": (449, 445),
    },
    "tournament": {
        "tournament_icon": (30, 71),
        "tournament_prestige": (330, 546),
        "tournament_collect_prize": (245, 731),
        "tournament_join": (245, 696),
    },
    "eggs": {
        "eggs_hatch": (35, 281),
    },
    "ad": {
        "ad_collect": (365, 616),
        "ad_no_thanks": (135, 616),
    },
    "artifacts": {
        "artifact_discover": (407, 604),
        "artifact_enchant": (410, 608),
        "artifact_purchase": (254, 554),
        "artifact_push_x": 375,
        "artifact_push_y": 20,
        "artifact_buy_multiplier": (410, 71),
        "artifact_buy_max": (50, 71),
        "artifact_percent_toggle": (303, 71),
    },
    "perks": {
        "perk_mega_boost": (356, 148),
        "perk_power_of_swiping": (356, 229),
        "perk_adrenaline_rush": (356, 310),
        "perk_make_it_rain": (356, 387),
        "perk_mana_potion": (356, 470),
        "perk_doom": (356, 548),
        "perk_clan_crate": (356, 627),
        "perk_okay": (326, 444),
        "perk_cancel": (150, 444),
        "perk_push_x": 396,
        "perk_push_y": 20,
    },
    "master_panel": {
        "master_level": (415, 136),
        "master_prestige": (405, 682),
        "master_prestige_confirm": (245, 675),
        "master_prestige_final": (330, 536),
        "master_screen_top": (240, 6),
        "master_achievements": (207, 503),
        "master_milestone_header": (245, 85),
        "master_milestone_collect": (382, 259),
        "master_skill_heavenly_strike": (415, 348),
        "master_skill_deadly_strike": (415, 421),
        "master_skill_hand_of_midas": (415, 574),
        "master_skill_fire_sword": (415, 574),
        "master_skill_war_cry": (415, 648),
        "master_skill_shadow_clone": (415, 723),
        "master_max_heavenly_strike": (268, 352),
        "master_max_deadly_strike": (268, 427),
        "master_max_hand_of_midas": (268, 503),
        "master_max_fire_sword": (268, 653),
        "master_max_war_cry": (268, 653),
        "master_max_shadow_clone": (268, 728),
        "master_can_level_heavenly_strike": (460, 319),
        "master_can_level_deadly_strike": (460, 395),
        "master_can_level_hand_of_midas": (460, 472),
        "master_can_level_fire_sword": (460, 546),
        "master_can_level_war_cry": (460, 623),
        "master_can_level_shadow_clone": (460, 698),
    },
    "heroes_panel": {
        "hero_drag_start": (328, 51),
        "hero_drag_end": (328, 610),
        "hero_level_heroes": (
            (405, 736), (405, 702), (405, 656), (405, 623), (405, 581),
            (405, 547), (405, 506), (405, 470), (405, 431), (405, 394),
            (405, 356), (405, 320), (405, 276), (405, 244), (405, 206),
            (405, 167), (405, 126), (405, 96), (405, 51),
        ),
        "hero_stats_collapsed": (135, 506),
        "hero_stats_expanded": (135, 71),
    },
    "equipment": {
        "equipment_equip": (409, 167),
        "equipment_tab_sword": (41, 86),
        "equipment_tab_headgear": (106, 86),
        "equipment_tab_cloak": (174, 86),
        "equipment_tab_aura": (240, 86),
        "equipment_tab_slash": (307, 86),
        "equipment_drag_start": (328, 165),
        "equipment_drag_end": (328, 610),
    },
}

GAME_REGIONS = {
    "perks": {
        "perk_purchase": (72, 290, 407, 405),
    },
    "statistics": {
        "statistic_regions": {
            "statistic_highest_stage_reached": (55, 440, 430, 461),
            "statistic_total_pet_level": (55, 461, 430, 481),
            "statistic_gold_earned": (55, 482, 430, 502),
            "statistic_taps": (55, 503, 430, 527),
            "statistic_titans_killed": (55, 525, 430, 545),
            "statistic_bosses_killed": (55, 546, 430, 566),
            "statistic_critical_hits": (55, 568, 430, 587),
            "statistic_chestersons_killed": (55, 589, 430, 652),
            "statistic_prestiges": (55, 611, 430, 674),
            "statistic_days_since_install": (55, 636, 430, 652),
            "statistic_play_time": (55, 653, 430, 674),
            "statistic_relics_earned": (55, 675, 430, 695),
            "statistic_fairies_tapped": (55, 697, 430, 717),
            "statistic_daily_achievements": (55, 716, 430, 739),
        },
    },
    "stage": {
        "stage_ocr": (215, 38, 268, 53),
    },
    "prestige": {
        "prestige_base": {
            "prestige_time_since": (301, 155, 380, 177),
            "prestige_advance_start": (136, 584, 212, 612),
        },
        "prestige_event": {
            "prestige_time_since": (301, 121, 380, 139),
            "prestige_advance_start": (138, 567, 191, 588),
        },
    },
    "skills": {
        "skill_regions": {
            "heavenly_strike": (0, 306, 480, 374),
            "deadly_strike": (0, 382, 480, 451),
            "hand_of_midas": (0, 457, 480, 526),
            "fire_sword": (0, 532, 480, 601),
            "war_cry": (0, 608, 480, 677),
            "shadow_clone": (0, 684, 480, 752),
        },
        "skill_level_regions": {
            "heavenly_strike": (70, 327, 115, 342),
            "deadly_strike": (70, 403, 115, 418),
            "hand_of_midas": (70, 478, 115, 493),
            "fire_sword": (70, 555, 115, 569),
            "war_cry": (70, 629, 115, 645),
            "shadow_clone": (70, 707, 115, 721),
        },
    },
    "clan": {
        "clan_info_name": (95, 15, 392, 54),
        "clan_info_code": (128, 746, 207, 766),
    },
    "raid": {
        "raid_attack_reset": (55, 719, 240, 737),
    },
    "artifacts": {
        "artifact_parse": (0, 57, 72, 763),
    },
    "heroes": {
        "hero_parse": [
            {
                "dps": (261, 120, 310, 141),
                "type": (300, 119, 322, 140),
            },
            {
                "dps": (260, 194, 308, 217),
                "type": (300, 194, 322, 217),
            },
            {
                "dps": (262, 271, 310, 291),
                "type": (298, 271, 324, 292),
            }
        ]
    },
    "equipment": {
        "gear_parse": [
            # SLOT 1.
            {
                "base": (0, 134, 472, 200),
                "locked": (40, 173, 73, 198),
                "bonus": (70, 180, 278, 198),
                "equip": (407, 166),
            },
            # SLOT 2.
            {
                "base": (0, 208, 476, 276),
                "locked": (40, 250, 73, 277),
                "bonus": (70, 256, 294, 276),
                "equip": (407, 244),
            },
            # SLOT 3.
            {
                "base": (0, 287, 476, 355),
                "locked": (40, 328, 73, 356),
                "bonus": (70, 335, 294, 353),
                "equip": (407, 322),
            },
            # SLOT 4.
            {
                "base": (0, 365, 476, 431),
                "locked": (40, 405, 73, 432),
                "bonus": (70, 411, 294, 431),
                "equip": (407, 400),
            },
            # SLOT 5.
            {
                "base": (0, 442, 476, 510),
                "locked": (40, 484, 73, 509),
                "bonus": (70, 488, 294, 508),
                "equip": (407, 476)
            },
            # SLOT 6.
            {
                "base": (0, 520, 476, 588),
                "locked": (40, 562, 73, 588),
                "bonus": (70, 567, 294, 587),
                "equip": (407, 554),
            },
            # SLOT 7.
            {
                "base": (0, 597, 476, 665),
                "locked": (40, 640, 73, 665),
                "bonus": (70, 644, 294, 664),
                "equip": (407, 632),
            },
            # SLOT 8.
            {
                "base": (0, 676, 476, 742),
                "locked": (40, 717, 73, 743),
                "bonus": (70, 723, 294, 743),
                "equip": (407, 710),
            },
        ],
    },
}

GAME_IMAGES = {
    "achievements": {
        "achievement_title": BOT_IMAGE_DIR + "/achievements/achievement_title.png",
        "achievement_daily_collect": BOT_IMAGE_DIR + "/achievements/achievement_daily_collect.png",
        "achievement_daily_watch": BOT_IMAGE_DIR + "/achievements/achievement_daily_watch.png",
        "achievement_vip_daily_collect": BOT_IMAGE_DIR + "/achievements/achievement_vip_daily_collect.png",
    },
    "ads": {
        "ad_collect": BOT_IMAGE_DIR + "/ads/ad_collect.png",
        "ad_watch": BOT_IMAGE_DIR + "/ads/ad_watch.png",
        "ad_no_thanks": BOT_IMAGE_DIR + "/ads/ad_no_thanks.png",
    },
    "artifacts": {
        "artifact_discovered": BOT_IMAGE_DIR + "/artifacts/artifact_discovered.png",
        "artifact_spend_max": BOT_IMAGE_DIR + "/artifacts/artifact_spend_max.png",
        "artifact_salvaged": BOT_IMAGE_DIR + "/artifacts/artifact_salvaged.png",
        "artifact_percent_on": BOT_IMAGE_DIR + "/artifacts/artifact_percent_on.png",
        "artifact_discover": BOT_IMAGE_DIR + "/artifacts/artifact_discover.png",
        "artifact_enchant": BOT_IMAGE_DIR + "/artifacts/artifact_enchant.png",
    },
    "daily_rewards": {
        "rewards_header": BOT_IMAGE_DIR + "/daily_rewards/rewards_header.png",
        "rewards_collect": BOT_IMAGE_DIR + "/daily_rewards/rewards_collect.png",
    },
    "inbox": {
        "inbox_header": BOT_IMAGE_DIR + "/inbox/inbox_header.png",
    },
    "equipment": {
        "equipment_crafting": BOT_IMAGE_DIR + "/equipment/equipment_crafting.png",
        "equipment_equip": BOT_IMAGE_DIR + "/equipment/equipment_equip.png",
        "equipment_locked": BOT_IMAGE_DIR + "/equipment/equipment_locked.png",
    },
    "generic": {
        "generic_app_icon": BOT_IMAGE_DIR + "/generic/generic_app_icon.png",
        "generic_artifacts_active": BOT_IMAGE_DIR + "/generic/generic_artifacts_active.png",
        "generic_buy_max": BOT_IMAGE_DIR + "/generic/generic_buy_max.png",
        "generic_buy_one": BOT_IMAGE_DIR + "/generic/generic_buy_one.png",
        "generic_buy_one_hundred": BOT_IMAGE_DIR + "/generic/generic_buy_one_hundred.png",
        "generic_buy_ten": BOT_IMAGE_DIR + "/generic/generic_buy_ten.png",
        "generic_collapse_panel": BOT_IMAGE_DIR + "/generic/generic_collapse_panel.png",
        "generic_expand_panel": BOT_IMAGE_DIR + "/generic/generic_expand_panel.png",
        "generic_equipment_active": BOT_IMAGE_DIR + "/generic/generic_equipment_active.png",
        "generic_exit_panel": BOT_IMAGE_DIR + "/generic/generic_exit_panel.png",
        "generic_heroes_active": BOT_IMAGE_DIR + "/generic/generic_heroes_active.png",
        "generic_large_exit_panel": BOT_IMAGE_DIR + "/generic/generic_large_exit_panel.png",
        "generic_master_active": BOT_IMAGE_DIR + "/generic/generic_master_active.png",
        "generic_max": BOT_IMAGE_DIR + "/generic/generic_max.png",
        "generic_pets_active": BOT_IMAGE_DIR + "/generic/generic_pets_active.png",
        "generic_shop_active": BOT_IMAGE_DIR + "/generic/generic_shop_active.png",
    },
    "heroes": {
        "hero_max_level": BOT_IMAGE_DIR + "/heroes/hero_max_level.png",
        "hero_maya_muerta": BOT_IMAGE_DIR + "/heroes/hero_maya_muerta.png",
        "hero_statistics": BOT_IMAGE_DIR + "/heroes/hero_statistics.png",
        "hero_story": BOT_IMAGE_DIR + "/heroes/hero_story.png",
        "hero_masteries": BOT_IMAGE_DIR + "/heroes/hero_masteries.png",
        "hero_zero_dps": BOT_IMAGE_DIR + "/heroes/hero_zero_dps.png",
        "hero_melee_type": BOT_IMAGE_DIR + "/heroes/hero_melee_type.png",
        "hero_spell_type": BOT_IMAGE_DIR + "/heroes/hero_spell_type.png",
        "hero_ranged_type": BOT_IMAGE_DIR + "/heroes/hero_ranged_type.png",
        "hero_bonus_melee": BOT_IMAGE_DIR + "/heroes/hero_bonus_melee.png",
        "hero_bonus_spell": BOT_IMAGE_DIR + "/heroes/hero_bonus_spell.png",
        "hero_bonus_ranged": BOT_IMAGE_DIR + "/heroes/hero_bonus_ranged.png",
    },
    "master": {
        "master_raid_cards": BOT_IMAGE_DIR + "/master/master_raid_cards.png",
        "master_achievements": BOT_IMAGE_DIR + "/master/master_achievements.png",
        "master_cancel_active_skill": BOT_IMAGE_DIR + "/master/master_cancel_active_skill.png",
        "master_confirm_prestige": BOT_IMAGE_DIR + "/master/master_confirm_prestige.png",
        "master_confirm_prestige_final": BOT_IMAGE_DIR + "/master/master_confirm_prestige_final.png",
        "master_heavenly_strike": BOT_IMAGE_DIR + "/master/master_heavenly_strike.png",
        "master_deadly_strike": BOT_IMAGE_DIR + "/master/master_deadly_strike.png",
        "master_hand_of_midas": BOT_IMAGE_DIR + "/master/master_hand_of_midas.png",
        "master_fire_sword": BOT_IMAGE_DIR + "/master/master_fire_sword.png",
        "master_war_cry": BOT_IMAGE_DIR + "/master/master_war_cry.png",
        "master_shadow_clone": BOT_IMAGE_DIR + "/master/master_shadow_clone.png",
        "master_inbox": BOT_IMAGE_DIR + "/master/master_inbox.png",
        "master_avatar": BOT_IMAGE_DIR + "/master/master_avatar.png",
        "master_prestige": BOT_IMAGE_DIR + "/master/master_prestige.png",
        "master_skill_level_zero": BOT_IMAGE_DIR + "/master/master_skill_level_zero.png",
        "master_skill_max_level": BOT_IMAGE_DIR + "/master/master_skill_max_level.png",
        "master_skill_tree": BOT_IMAGE_DIR + "/master/master_skill_tree.png",
        "master_unlock_at": BOT_IMAGE_DIR + "/master/master_unlock_at.png",
        "master_silent_march": BOT_IMAGE_DIR + "/master/mater_silent_march.png",
    },
    "no_panels": {
        "no_panel_clan_raid_ready": BOT_IMAGE_DIR + "/no_panels/no_panel_clan_raid_ready.png",
        "no_panel_clan_no_raid": BOT_IMAGE_DIR + "/no_panels/no_panel_clan_no_raid.png",
        "no_panel_daily_reward": BOT_IMAGE_DIR + "/no_panels/no_panel_daily_reward.png",
        "no_panel_fight_boss": BOT_IMAGE_DIR + "/no_panels/no_panel_fight_boss.png",
        "no_panel_hatch_egg": BOT_IMAGE_DIR + "/no_panels/no_panel_hatch_egg.png",
        "no_panel_leave_boss": BOT_IMAGE_DIR + "/no_panels/no_panel_leave_boss.png",
        "no_panel_settings": BOT_IMAGE_DIR + "/no_panels/no_panel_settings.png",
        "no_panel_tournament": BOT_IMAGE_DIR + "/no_panels/no_panel_tournament.png",
        "no_panel_pet_damage": BOT_IMAGE_DIR + "/no_panels/no_panel_pet_damage.png",
        "no_panel_master_damage": BOT_IMAGE_DIR + "/no_panels/no_panel_master_damage.png",
    },
    "perks": {
        "perk_mega_boost": BOT_IMAGE_DIR + "/perks/perk_mega_boost.png",
        "perk_power_of_swiping": BOT_IMAGE_DIR + "/perks/perk_power_of_swiping.png",
        "perk_adrenaline_rush": BOT_IMAGE_DIR + "/perks/perk_adrenaline_rush.png",
        "perk_make_it_rain": BOT_IMAGE_DIR + "/perks/perk_make_it_rain.png",
        "perk_mana_potion": BOT_IMAGE_DIR + "/perks/perk_mana_potion.png",
        "perk_doom": BOT_IMAGE_DIR + "/perks/perk_doom.png",
        "perk_clan_crate": BOT_IMAGE_DIR + "/perks/perk_clan_crate.png",
        "perk_diamond": BOT_IMAGE_DIR + "/perks/perk_diamond.png",
        "perk_perks_header": BOT_IMAGE_DIR + "/perks/perk_perks_header.png",
        "perk_perk_header": BOT_IMAGE_DIR + "/perks/perk_perk_header.png",
        "perk_vip_watch": BOT_IMAGE_DIR + "/perks/perk_vip_watch.png",
    },
    "welcome": {
        "welcome_header": BOT_IMAGE_DIR + "/welcome/welcome_header.png",
        "welcome_collect_no_vip": BOT_IMAGE_DIR + "/welcome/welcome_collect_no_vip.png",
        "welcome_collect_vip": BOT_IMAGE_DIR + "/welcome/welcome_collect_vip.png",
    },
    "tournament": {
        "tournament_join": BOT_IMAGE_DIR + "/tournament/tournament_join.png",
        "tournament_collect": BOT_IMAGE_DIR + "/tournament/tournament_collect.png",
    },
    "clan": {
        "clan_header": BOT_IMAGE_DIR + "/clan/clan_header.png",
        "clan_info": BOT_IMAGE_DIR + "/clan/clan_info.png",
    },
    "clan_crate": {
        "crate_okay": BOT_IMAGE_DIR + "/clan_crate/crate_okay.png",
    },
    "pets": {
        "pet_next_egg": BOT_IMAGE_DIR + "/pets/pet_next_egg.png",
    },
    "shop": {
        "shop_keeper": BOT_IMAGE_DIR + "/shop/shop_keeper.png",
    },
    "rate": {
        "rate_icon": BOT_IMAGE_DIR + "/rate/rate_icon.png",
    },
    "raid": {
        "raid_fight": BOT_IMAGE_DIR + "/raids/raid_fight.png",
    },
    "statistics": {
        "statistic_title": BOT_IMAGE_DIR + "/statistics/statistic_title.png",
    }
}

# Create a dictionary that contains information about all of the data that should be present
# for use with bot artifact parsing and upgrading, as well as being present in the database
# and always keeping our artifacts totally up to date.
ARTIFACT_TIER_MAP = {
    "S": {
        "book_of_shadows": (ARTIFACT_IMAGE_DIR + "/book_of_shadows.png", 22),
        "stone_of_the_valrunes": (ARTIFACT_IMAGE_DIR + "/stone_of_the_valrunes.png", 2),
        "flute_of_the_soloist": (ARTIFACT_IMAGE_DIR + "/flute_of_the_soloist.png", 84),
        "heart_of_storms": (ARTIFACT_IMAGE_DIR + "/heart_of_storms.png", 52),
        "ring_of_calisto": (ARTIFACT_IMAGE_DIR + "/ring_of_calisto.png", 40),
        "invaders_gjalarhorn": (ARTIFACT_IMAGE_DIR + "/invaders_gjalarhorn.png", 47),
        "boots_of_hermes": (ARTIFACT_IMAGE_DIR + "/boots_of_hermes.png", 70),
    },
    "A": {
        "charged_card": (ARTIFACT_IMAGE_DIR + "/charged_card.png", 95),
        "book_of_prophecy": (ARTIFACT_IMAGE_DIR + "/book_of_prophecy.png", 20),
        "khrysos_bowl": (ARTIFACT_IMAGE_DIR + "/khrysos_bowl.png", 66),
        "the_bronzed_compass": (ARTIFACT_IMAGE_DIR + "/the_bronzed_compass.png", 82),
        "evergrowing_stack": (ARTIFACT_IMAGE_DIR + "/evergrowing_stack.png", 94),
        "heavenly_sword": (ARTIFACT_IMAGE_DIR + "/heavenly_sword.png", 26),
        "divine_retribution": (ARTIFACT_IMAGE_DIR + "/divine_retribution.png", 31),
        "drunken_hammer": (ARTIFACT_IMAGE_DIR + "/drunken_hammer.png", 29),
        "samosek_sword": (ARTIFACT_IMAGE_DIR + "/samosek_sword.png", 51),
        "the_retaliator": (ARTIFACT_IMAGE_DIR + "/the_retaliator.png", 59),
        "stryfe's_peace": (ARTIFACT_IMAGE_DIR + "/stryfes_peace.png", 83),
        "hero's_blade": (ARTIFACT_IMAGE_DIR + "/heros_blade.png", 35),
        "the_sword_of_storms": (ARTIFACT_IMAGE_DIR + "/the_sword_of_storms.png", 32),
        "furies_bow": (ARTIFACT_IMAGE_DIR + "/furies_bow.png", 33),
        "charm_of_the_ancient": (ARTIFACT_IMAGE_DIR + "/charm_of_the_ancient.png", 34),
        "tiny_titan_tree": (ARTIFACT_IMAGE_DIR + "/tiny_titan_tree.png", 61),
        "helm_of_hermes": (ARTIFACT_IMAGE_DIR + "/helm_of_hermes.png", 62),
        "o'ryans_charm": (ARTIFACT_IMAGE_DIR + "/oryans_charm.png", 64),
        "apollo_orb": (ARTIFACT_IMAGE_DIR + "/apollo_orb.png", 53),
        "earrings_of_portara": (ARTIFACT_IMAGE_DIR + "/earrings_of_portara.png", 67),
        "helheim_skull": (ARTIFACT_IMAGE_DIR + "/helheim_skull.png", 56),
        "oath's_burden": (ARTIFACT_IMAGE_DIR + "/oaths_burden.png", 75),
        "crown_of_the_constellation": (ARTIFACT_IMAGE_DIR + "/crown_of_the_constellation.png", 76),
        "titania's_sceptre": (ARTIFACT_IMAGE_DIR + "/titanias_sceptre.png", 77),
        "blade_of_damocles": (ARTIFACT_IMAGE_DIR + "/blade_of_damocles.png", 25),
        "helmet_of_madness": (ARTIFACT_IMAGE_DIR + "/helmet_of_madness.png", 17),
        "titanium_plating": (ARTIFACT_IMAGE_DIR + "/titanium_plating.png", 23),
        "moonlight_bracelet": (ARTIFACT_IMAGE_DIR + "/moonlight_bracelet.png", 73),
        "amethyst_staff": (ARTIFACT_IMAGE_DIR + "/amethyst_staff.png", 28),
        "spearit's_vigil": (ARTIFACT_IMAGE_DIR + "/spearits_vigil.png", 87),
        "sword_of_the_royals": (ARTIFACT_IMAGE_DIR + "/sword_of_the_royals.png", 86),
        "the_cobalt_plate": (ARTIFACT_IMAGE_DIR + "/the_cobalt_plate.png", 88),
        "sigils_of_judgement": (ARTIFACT_IMAGE_DIR + "/sigils_of_judgement.png", 89),
        "foilage_of_the_keeper": (ARTIFACT_IMAGE_DIR + "/foilage_of_the_keeper.png", 90),
        "laborer's_pendant": (ARTIFACT_IMAGE_DIR + "/laborers_pendant.png", 9),
        "bringer_of_ragnarok": (ARTIFACT_IMAGE_DIR + "/bringer_of_ragnarok.png", 10),
        "parchment_of_foresight": (ARTIFACT_IMAGE_DIR + "/parchment_of_foresight.png", 7),
        "unbound_gauntlet": (ARTIFACT_IMAGE_DIR + "/unbound_gauntlet.png", 74),
        "lucky_foot_of_al-mi-raj": (ARTIFACT_IMAGE_DIR + "/lucky_foot_of_al-mi-raj.png", 69),
        "morgelai_sword": (ARTIFACT_IMAGE_DIR + "/morgelai_sword.png", 71),
        "ringing_stone": (ARTIFACT_IMAGE_DIR + "/ringing_stone.png", 91),
        "quill_of_scrolls": (ARTIFACT_IMAGE_DIR + "/quill_of_scrolls.png", 92),
        "old_king's_stamp": (ARTIFACT_IMAGE_DIR + "/old_kings_stamp.png", 93),
        "the_magnifier": (ARTIFACT_IMAGE_DIR + "/the_magnifier.png", 80),
        "the_treasure_of_fergus": (ARTIFACT_IMAGE_DIR + "/the_treasure_of_fergus.png", 81),
        "the_white_dwarf": (ARTIFACT_IMAGE_DIR + "/the_white_dwarf.png", 85),
    },
    "B": {
        "chest_of_contentment": (ARTIFACT_IMAGE_DIR + "/chest_of_contentment.png", 19),
        "heroic_shield": (ARTIFACT_IMAGE_DIR + "/heroic_shield.png", 1),
        "zakynthos_coin": (ARTIFACT_IMAGE_DIR + "/zakynthos_coin.png", 43),
        "great_fay_medallion": (ARTIFACT_IMAGE_DIR + "/great_fay_medallion.png", 44),
        "neko_sculpture": (ARTIFACT_IMAGE_DIR + "/neko_sculpture.png", 45),
        "coins_of_ebizu": (ARTIFACT_IMAGE_DIR + "/coins_of_ebizu.png", 79),
        "fruit_of_eden": (ARTIFACT_IMAGE_DIR + "/fruit_of_eden.png", 38),
        "influential_elixir": (ARTIFACT_IMAGE_DIR + "/influential_elixir.png", 30),
        "avian_feather": (ARTIFACT_IMAGE_DIR + "/avian_feather.png", 42),
        "fagin's_grip": (ARTIFACT_IMAGE_DIR + "/fagins_grip.png", 78),
        "titan's_mask": (ARTIFACT_IMAGE_DIR + "/titans_mask.png", 11),
        "royal_toxin": (ARTIFACT_IMAGE_DIR + "/royal_toxin.png", 41),
        "elixir_of_eden": (ARTIFACT_IMAGE_DIR + "/elixir_of_eden.png", 6),
        "hourglass_of_the_impatient": (ARTIFACT_IMAGE_DIR + "/hourglass_of_the_impatient.png", 65),
        "phantom_timepiece": (ARTIFACT_IMAGE_DIR + "/phantom_timepiece.png", 48),
        "infinity_pendulum": (ARTIFACT_IMAGE_DIR + "/infinity_pendulum.png", 36),
        "glove_of_kuma": (ARTIFACT_IMAGE_DIR + "/glove_of_kuma.png", 27),
        "titan_spear": (ARTIFACT_IMAGE_DIR + "/titan_spear.png", 39),
        "oak_staff": (ARTIFACT_IMAGE_DIR + "/oak_staff.png", 37),
        "the_arcana_cloak": (ARTIFACT_IMAGE_DIR + "/the_arcana_cloak.png", 3),
        "hunter's_ointment": (ARTIFACT_IMAGE_DIR + "/hunters_ointment.png", 8),
        "axe_of_muerte": (ARTIFACT_IMAGE_DIR + "/axe_of_muerte.png", 4),
        "the_master's_sword": (ARTIFACT_IMAGE_DIR + "/the_masters_sword.png", 49),
        "mystical_beans_of_senzu": (ARTIFACT_IMAGE_DIR + "/mystical_beans_of_senzu.png", 68),
    },
    "C": {
        "corrupted_rune_heart": (ARTIFACT_IMAGE_DIR + "/corrupted_rune_heart.png", 46),
        "durendal_sword": (ARTIFACT_IMAGE_DIR + "/durendal_sword.png", 55),
        "forbidden_scroll": (ARTIFACT_IMAGE_DIR + "/forbidden_scroll.png", 13),
        "ring_of_fealty": (ARTIFACT_IMAGE_DIR + "/ring_of_fealty.png", 15),
        "glacial_axe": (ARTIFACT_IMAGE_DIR + "/glacial_axe.png", 16),
        "aegis": (ARTIFACT_IMAGE_DIR + "/aegis.png", 14),
        "swamp_gauntlet": (ARTIFACT_IMAGE_DIR + "/swamp_gauntlet.png", 12),
        "ambrosia_elixir": (ARTIFACT_IMAGE_DIR + "/ambrosia_elixir.png", 50),
        "mystic_staff": (ARTIFACT_IMAGE_DIR + "/mystic_staff.png", 58),
        "egg_of_fortune": (ARTIFACT_IMAGE_DIR + "/egg_of_fortune.png", 18),
        "divine_chalice": (ARTIFACT_IMAGE_DIR + "/divine_chalice.png", 21),
        "invader's_shield": (ARTIFACT_IMAGE_DIR + "/invaders_shield.png", 5),
        "essence_of_kitsune": (ARTIFACT_IMAGE_DIR + "/essence_of_kitsune.png", 54),
        "oberon_pendant": (ARTIFACT_IMAGE_DIR + "/oberon_pendant.png", 72),
        "lost_king's_mask": (ARTIFACT_IMAGE_DIR + "/lost_kings_mask.png", 63),
        "staff_of_radiance": (ARTIFACT_IMAGE_DIR + "/staff_of_radiance.png", 24),
        "aram_spear": (ARTIFACT_IMAGE_DIR + "/aram_spear.png", 57),
        "ward_of_the_darkness": (ARTIFACT_IMAGE_DIR + "/ward_of_the_darkness.png", 60),
    },
}

# Create an additional dictionary that only contains our artifacts, without the
# tiers associated with each, mapped to the image path for each one.
ARTIFACTS = {
    k1: v1[0] for k, v in ARTIFACT_TIER_MAP.items() for k1, v1 in v.items()
}

# Creating a list of all artifacts in game that contain a max level. These can be safely
# ignored when we are upgrading. Since there's no need to upgrade an artifact that
# can no longer be levelled.
MAX_LEVEL_ARTIFACTS = [
    "hourglass_of_the_impatient", "phantom_timepiece", "forbidden_scroll", "ring_of_fealty",
    "glacial_axe", "aegis", "swamp_gauntlet", "infinity_pendulum", "glove_of_kuma", "titan_spear",
    "oak_staff", "the_arcana_cloak", "hunter's_ointment", "ambrosia_elixir", "mystic_staff",
    "mystical_beans_of_senzu", "egg_of_fortune", "divine_chalice", "invader's_shield", "axe_of_muerte",
    "essence_of_the_kitsune", "boots_of_hermes", "unbound_gauntlet", "oberon_pendant",
    "lucky_foot_of_al-mi-raj", "lost_king's_mask", "staff_of_radiance", "morgelai_sword", "ringing_stone",
    "quill_of_scrolls", "old_king's_stamp", "the_master's_sword", "the_magnifier", "the_treasure_of_fergus",
    "the_white_dwarf", "aram_spear", "ward_of_the_darkness",
]

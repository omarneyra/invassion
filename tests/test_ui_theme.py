# tests/test_ui_theme.py
# Unit tests for logic/ui_theme.py (Sci-Fi Tactical UI & Palette).

import unittest
from logic.ui_theme import (
    get_scifi_hud_colors,
    get_planetary_surface_palette,
    format_energy_display,
    format_wave_threat_alert,
    calculate_health_bar_color,
    format_structure_inspector_data,
    format_command_button_data,
)

class TestUITheme(unittest.TestCase):
    def test_scifi_hud_colors_palette_integrity(self):
        colors = get_scifi_hud_colors()
        self.assertIn("bg_topbar", colors)
        self.assertIn("border_button_hover", colors)
        self.assertIn("hp_bar_fill_high", colors)
        self.assertTrue(colors["border_button_hover"].startswith("#"))

    def test_planetary_surface_palette(self):
        pal = get_planetary_surface_palette()
        self.assertIn("ocean_deep", pal)
        self.assertIn("continental_rock", pal)
        self.assertIn("atmosphere_rim", pal)
        self.assertGreater(pal["normal_bump_strength"], 1.0)
        self.assertLess(pal["roughness_water"], pal["roughness_land"])

    def test_format_energy_display(self):
        normal = format_energy_display(100.0, 5.0)
        self.assertEqual(normal["label"], "ENERGY: 100 E")
        self.assertEqual(normal["rate_label"], "(+5.0/s)")
        self.assertFalse(normal["is_low"])

        low = format_energy_display(15.0, 2.0)
        self.assertTrue(low["is_low"])
        self.assertEqual(low["color"], "#ef4444")

    def test_format_wave_threat_alert(self):
        # Inactive wave countdown
        calm = format_wave_threat_alert(False, 1, 15.0, 0)
        self.assertEqual(calm["badge"], "[ SURVEILLANCE ]")
        self.assertEqual(calm["text"], "NEXT WAVE #1 IN T-15s")
        self.assertFalse(calm["is_critical"])

        # Imminent threat
        imminent = format_wave_threat_alert(False, 2, 3.0, 0)
        self.assertEqual(imminent["badge"], "[ THREAT IMMINENT ]")
        self.assertTrue(imminent["is_critical"])

        # Active incursion
        active = format_wave_threat_alert(True, 3, 0.0, 5)
        self.assertEqual(active["badge"], "[ ACTIVE INCURSION ]")
        self.assertIn("5 HOSTILES ACTIVE", active["text"])
        self.assertEqual(active["progress_pct"], 100.0)

    def test_calculate_health_bar_color(self):
        self.assertEqual(calculate_health_bar_color(100, 100), "#22c55e")
        self.assertEqual(calculate_health_bar_color(50, 100), "#f59e0b")
        self.assertEqual(calculate_health_bar_color(20, 100), "#ef4444")
        self.assertEqual(calculate_health_bar_color(0, 100), "#ef4444")

    def test_format_structure_inspector_data_unselected(self):
        data = format_structure_inspector_data(-1, {}, {})
        self.assertFalse(data["is_selected"])
        self.assertEqual(data["structure_tag"], "[ UNSELECTED ]")
        self.assertEqual(data["portrait_key"], "empty")

    def test_format_structure_inspector_data_turret(self):
        factions = {
            1: {"name": "Solarian Federation", "color": "#22c55e"}
        }
        node_data = {
            "controller": 1,
            "building": {
                "type": "turret",
                "hp": 350.0,
                "max_hp": 400.0,
                "damage": 35.0,
                "cooldown": 0.8,
                "attack_range_hops": 2,
            }
        }
        res = format_structure_inspector_data(12, node_data, factions)
        self.assertTrue(res["is_selected"])
        self.assertEqual(res["structure_tag"], "[ TURRET ]")
        self.assertEqual(res["structure_name"], "PULSE DEFENSE CANNON")
        self.assertEqual(res["portrait_key"], "turret")
        self.assertEqual(res["hp"], 350)
        self.assertIn("350 / 400 HP", res["hp_text"])
        self.assertIn("FIREPOWER: 35 DMG", res["stats_line_2"])

    def test_format_structure_inspector_portraits_all_types(self):
        factions = {1: {"name": "Solarian Federation", "color": "#22c55e"}}
        # Base
        base_res = format_structure_inspector_data(0, {"controller": 1, "building": {"type": "base", "hp": 1500, "max_hp": 1500}}, factions)
        self.assertEqual(base_res["portrait_key"], "base")
        # Harvester
        harv_res = format_structure_inspector_data(1, {"controller": 1, "building": {"type": "harvester", "hp": 250, "max_hp": 250}}, factions)
        self.assertEqual(harv_res["portrait_key"], "harvester")
        # Wall
        wall_res = format_structure_inspector_data(2, {"controller": 1, "building": {"type": "wall", "hp": 400, "max_hp": 400}}, factions)
        self.assertEqual(wall_res["portrait_key"], "wall")
        # Empty unclaimed node
        empty_res = format_structure_inspector_data(3, {"controller": 0}, factions)
        self.assertEqual(empty_res["portrait_key"], "empty")

    def test_format_command_button_data(self):
        btn = format_command_button_data("turret", 100.0, 75.0, 0.0, False)
        self.assertEqual(btn["title"], "TURRET")
        self.assertEqual(btn["hotkey"], "[3]")
        self.assertTrue(btn["is_enabled"])
        self.assertIn("75 E", btn["cost_label"])

        btn_unaffordable = format_command_button_data("turret", 50.0, 75.0, 0.0, False)
        self.assertFalse(btn_unaffordable["is_enabled"])

        btn_cooldown = format_command_button_data("assault", 100.0, 85.0, 4.2, False)
        self.assertFalse(btn_cooldown["is_enabled"])
        self.assertIn("RECHARGE", btn_cooldown["cost_label"])

if __name__ == "__main__":
    unittest.main()

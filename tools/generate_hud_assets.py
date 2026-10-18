# scratch/generate_hud_assets.py
# High-DPI procedural Sci-Fi RTS icon and portrait generator using PIL.
# Generates razor-sharp, beveled, textured icons with 4x supersampling (anti-aliased).

import os
import math
from PIL import Image, ImageDraw, ImageFilter

ASSETS_DIR = "/home/xor/Proyectos/invassion/assets/ui"
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
PORTRAITS_DIR = os.path.join(ASSETS_DIR, "portraits")
FRAMES_DIR = os.path.join(ASSETS_DIR, "frames")

os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(PORTRAITS_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

def create_base_card(size=256, border_color=(0, 229, 255), fill_color=(8, 16, 32)):
    """Creates a metallic beveled sci-fi button base with dark gloss gradient."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Beveled background polygon with chamfered corners
    chamfer = size * 0.1
    pts = [
        (chamfer, 0), (size - chamfer, 0),
        (size, chamfer), (size, size - chamfer),
        (size - chamfer, size), (chamfer, size),
        (0, size - chamfer), (0, chamfer)
    ]
    
    # Outer dark shadow
    draw.polygon(pts, fill=(4, 8, 16, 240))

    # Inner gradient / dark gloss
    inset = size * 0.04
    pts_in = [
        (chamfer + inset, inset), (size - chamfer - inset, inset),
        (size - inset, chamfer + inset), (size - inset, size - chamfer - inset),
        (size - chamfer - inset, size - inset), (chamfer + inset, size - inset),
        (inset, size - chamfer - inset), (inset, chamfer + inset)
    ]
    draw.polygon(pts_in, fill=fill_color)

    # Subtle tech grid lines in background
    grid_col = (border_color[0] // 5, border_color[1] // 5, border_color[2] // 5, 60)
    step = int(size * 0.15)
    for x in range(step, size, step):
        draw.line([(x, inset), (x, size - inset)], fill=grid_col, width=1)
    for y in range(step, size, step):
        draw.line([(inset, y), (size - inset, y)], fill=grid_col, width=1)

    # Glowing outer border
    border_rgba = (border_color[0], border_color[1], border_color[2], 220)
    draw.polygon(pts_in, outline=border_rgba, width=int(size * 0.035))

    # Metallic corner highlight studs
    stud_col = (255, 255, 255, 200)
    for p in [(chamfer, chamfer), (size - chamfer, chamfer), (chamfer, size - chamfer), (size - chamfer, size - chamfer)]:
        r = size * 0.02
        draw.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=stud_col)

    return img

def render_icon_wall(target_size=64):
    """Reinforced Plasma Barricade with glowing energy shield."""
    S = 256
    img = create_base_card(S, border_color=(0, 229, 255), fill_color=(6, 18, 36, 250))
    draw = ImageDraw.Draw(img)

    cx, cy = S // 2, S // 2

    # Left & Right Steel Pylons
    p_w = S * 0.12
    p_h = S * 0.55
    draw.rectangle([cx - S * 0.38, cy - p_h/2, cx - S * 0.38 + p_w, cy + p_h/2], fill=(70, 95, 125), outline=(140, 180, 215), width=3)
    draw.rectangle([cx + S * 0.38 - p_w, cy - p_h/2, cx + S * 0.38, cy + p_h/2], fill=(70, 95, 125), outline=(140, 180, 215), width=3)

    # Glowing Pylon Cores
    draw.rectangle([cx - S * 0.35, cy - S*0.15, cx - S * 0.35 + p_w*0.5, cy + S*0.15], fill=(0, 240, 255))
    draw.rectangle([cx + S * 0.35 - p_w*0.5, cy - S*0.15, cx + S * 0.35, cy + S*0.15], fill=(0, 240, 255))

    # Hexagonal Forcefield Barrier in center
    shield_w = S * 0.5
    shield_h = S * 0.42
    pts_shield = [
        (cx - shield_w/2, cy - shield_h/4),
        (cx, cy - shield_h/2),
        (cx + shield_w/2, cy - shield_h/4),
        (cx + shield_w/2, cy + shield_h/4),
        (cx, cy + shield_h/2),
        (cx - shield_w/2, cy + shield_h/4)
    ]
    draw.polygon(pts_shield, fill=(0, 180, 255, 120), outline=(0, 255, 255, 240), width=4)

    # Internal energy grid
    draw.line([(cx - shield_w/2, cy), (cx + shield_w/2, cy)], fill=(255, 255, 255, 180), width=3)
    draw.line([(cx, cy - shield_h/2), (cx, cy + shield_h/2)], fill=(255, 255, 255, 180), width=3)

    # Downsample
    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def render_icon_harvester(target_size=64):
    """Quantum Energy Extractor / Refinery Drill with amber energy conduit."""
    S = 256
    img = create_base_card(S, border_color=(245, 158, 11), fill_color=(26, 18, 6, 250))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2

    # Industrial Tripod Legs
    draw.line([(cx - S*0.35, cy + S*0.35), (cx - S*0.15, cy + S*0.05)], fill=(120, 110, 100), width=7)
    draw.line([(cx + S*0.35, cy + S*0.35), (cx + S*0.15, cy + S*0.05)], fill=(120, 110, 100), width=7)
    draw.line([(cx, cy + S*0.38), (cx, cy + S*0.05)], fill=(160, 150, 140), width=8)

    # Main Refinery Derrick Body
    derrick_pts = [
        (cx - S*0.22, cy + S*0.1),
        (cx - S*0.12, cy - S*0.28),
        (cx + S*0.12, cy - S*0.28),
        (cx + S*0.22, cy + S*0.1)
    ]
    draw.polygon(derrick_pts, fill=(90, 80, 70), outline=(210, 170, 70), width=3)

    # Glowing Extraction Core Sphere
    r = S * 0.16
    draw.ellipse([cx - r, cy - S*0.12 - r, cx + r, cy - S*0.12 + r], fill=(255, 180, 20), outline=(255, 240, 150), width=4)

    # Laser Drill Beam into Ground
    draw.polygon([(cx - S*0.06, cy + S*0.08), (cx + S*0.06, cy + S*0.08), (cx + S*0.15, cy + S*0.4), (cx - S*0.15, cy + S*0.4)], fill=(255, 215, 0, 180))
    draw.line([(cx, cy + S*0.08), (cx, cy + S*0.4)], fill=(255, 255, 255), width=4)

    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def render_icon_turret(target_size=64):
    """Twin-Barrel Rapid Pulse Defense Cannon with targeting laser."""
    S = 256
    img = create_base_card(S, border_color=(34, 197, 94), fill_color=(8, 24, 16, 250))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2

    # Heavy Turret Base Platform
    draw.ellipse([cx - S*0.36, cy + S*0.08, cx + S*0.36, cy + S*0.38], fill=(50, 70, 60), outline=(100, 160, 120), width=4)

    # Armored Rotating Turret Dome
    draw.ellipse([cx - S*0.24, cy - S*0.12, cx + S*0.24, cy + S*0.22], fill=(90, 120, 105), outline=(180, 230, 200), width=4)

    # Twin Plasma Barrels pointing upward-right
    b_len = S * 0.42
    b_thick = S * 0.08
    angle = math.radians(-35)
    dx = math.cos(angle)
    dy = math.sin(angle)

    for offset in [-S*0.08, S*0.08]:
        bx = cx + offset * (-dy)
        by = cy - S*0.02 + offset * dx
        draw.line([(bx, by), (bx + dx * b_len, by + dy * b_len)], fill=(140, 160, 150), width=int(b_thick))
        draw.line([(bx + dx * (b_len - S*0.08), by + dy * (b_len - S*0.08)), (bx + dx * b_len, by + dy * b_len)], fill=(60, 240, 120), width=int(b_thick - 2))

    # Muzzle Energy Charge Glow
    for offset in [-S*0.08, S*0.08]:
        bx = cx + offset * (-dy) + dx * b_len
        by = cy - S*0.02 + offset * dx + dy * b_len
        r = S * 0.06
        draw.ellipse([bx-r, by-r, bx+r, by+r], fill=(0, 255, 140, 220))

    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def render_icon_assault(target_size=64):
    """Armored Strike Squad / Mech Assault Battalion banner."""
    S = 256
    img = create_base_card(S, border_color=(239, 68, 68), fill_color=(28, 8, 8, 250))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2

    # Tactical Chevron Wings
    draw.polygon([(cx - S*0.38, cy - S*0.1), (cx, cy - S*0.35), (cx + S*0.38, cy - S*0.1), (cx, cy - S*0.2)], fill=(180, 40, 40), outline=(255, 100, 100), width=3)
    draw.polygon([(cx - S*0.32, cy + S*0.05), (cx, cy - S*0.15), (cx + S*0.32, cy + S*0.05), (cx, cy - S*0.02)], fill=(220, 50, 50), outline=(255, 140, 140), width=3)

    # Central Armored Mech Visor / Head
    visor_pts = [
        (cx - S*0.18, cy + S*0.02),
        (cx + S*0.18, cy + S*0.02),
        (cx + S*0.12, cy + S*0.35),
        (cx - S*0.12, cy + S*0.35)
    ]
    draw.polygon(visor_pts, fill=(60, 65, 75), outline=(200, 210, 225), width=4)

    # Glowing Cyan/Red Tactical Visor Slit
    draw.line([(cx - S*0.12, cy + S*0.12), (cx + S*0.12, cy + S*0.12)], fill=(0, 240, 255), width=6)
    draw.line([(cx - S*0.06, cy + S*0.22), (cx + S*0.06, cy + S*0.22)], fill=(255, 50, 50), width=4)

    # Heavy Cross-Rifles behind
    draw.line([(cx - S*0.35, cy + S*0.35), (cx + S*0.35, cy - S*0.2)], fill=(160, 170, 180), width=5)
    draw.line([(cx + S*0.35, cy + S*0.35), (cx - S*0.35, cy - S*0.2)], fill=(160, 170, 180), width=5)

    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def render_icon_wave(target_size=64):
    """Hostile Incursion / Threat Alert Skull."""
    S = 256
    img = create_base_card(S, border_color=(168, 85, 247), fill_color=(20, 8, 30, 250))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2

    # Biomechanical Skull Dome
    draw.ellipse([cx - S*0.26, cy - S*0.32, cx + S*0.26, cy + S*0.12], fill=(160, 130, 180), outline=(220, 180, 255), width=4)

    # Jaw Bone
    draw.rectangle([cx - S*0.14, cy + S*0.08, cx + S*0.14, cy + S*0.3], fill=(130, 100, 150), outline=(200, 160, 230), width=3)
    # Teeth slits
    for i in range(-2, 3):
        draw.line([(cx + i*S*0.05, cy + S*0.12), (cx + i*S*0.05, cy + S*0.28)], fill=(30, 10, 45), width=2)

    # Glowing Menacing Eye Sockets
    draw.ellipse([cx - S*0.18, cy - S*0.12, cx - S*0.04, cy + S*0.04], fill=(255, 0, 100))
    draw.ellipse([cx + S*0.04, cy - S*0.12, cx + S*0.18, cy + S*0.04], fill=(255, 0, 100))

    # Bio-Spikes radiating from sides
    draw.line([(cx - S*0.26, cy - S*0.1), (cx - S*0.42, cy - S*0.22)], fill=(200, 100, 255), width=6)
    draw.line([(cx + S*0.26, cy - S*0.1), (cx + S*0.42, cy - S*0.22)], fill=(200, 100, 255), width=6)

    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def render_icon_base(target_size=64):
    """Planetary Command Citadel / Headquarters."""
    S = 256
    img = create_base_card(S, border_color=(56, 189, 248), fill_color=(8, 20, 36, 250))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2

    # Heavy Fortified Base Tier
    draw.polygon([(cx - S*0.36, cy + S*0.32), (cx + S*0.36, cy + S*0.32), (cx + S*0.28, cy + S*0.12), (cx - S*0.28, cy + S*0.12)], fill=(60, 80, 100), outline=(130, 180, 220), width=4)

    # Command Tower Tier
    draw.polygon([(cx - S*0.2, cy + S*0.12), (cx + S*0.2, cy + S*0.12), (cx + S*0.14, cy - S*0.16), (cx - S*0.14, cy - S*0.16)], fill=(80, 110, 140), outline=(180, 220, 255), width=4)

    # Central Blue Planetary Reactor
    r = S * 0.1
    draw.ellipse([cx - r, cy - S*0.02 - r, cx + r, cy - S*0.02 + r], fill=(0, 230, 255), outline=(255, 255, 255), width=3)

    # Communication & Defense Spire Antenna
    draw.line([(cx, cy - S*0.16), (cx, cy - S*0.38)], fill=(200, 220, 240), width=6)
    draw.ellipse([cx - S*0.05, cy - S*0.42, cx + S*0.05, cy - S*0.32], fill=(0, 255, 200))

    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def render_icon_tech(target_size=64):
    """Cybernetic Research & Tech Tree Archive."""
    S = 256
    img = create_base_card(S, border_color=(45, 212, 191), fill_color=(6, 24, 24, 250))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2

    # Quantum Atomic Orbital Rings
    for a in [0, 60, 120]:
        rad = math.radians(a)
        w, h = S * 0.38, S * 0.16
        pts = []
        for step in range(0, 360, 10):
            t = math.radians(step)
            x0 = w * math.cos(t)
            y0 = h * math.sin(t)
            xr = cx + x0 * math.cos(rad) - y0 * math.sin(rad)
            yr = cy + x0 * math.sin(rad) + y0 * math.cos(rad)
            pts.append((xr, yr))
        draw.polygon(pts, outline=(45, 212, 191, 160), width=3)

    # Central Quantum Processor Core
    r = S * 0.12
    draw.rectangle([cx - r, cy - r, cx + r, cy + r], fill=(20, 160, 140), outline=(150, 255, 235), width=3)
    draw.ellipse([cx - r/2, cy - r/2, cx + r/2, cy + r/2], fill=(255, 255, 255))

    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def render_icon_energy(target_size=64):
    """Ion Energy Battery Cell."""
    S = 256
    img = create_base_card(S, border_color=(34, 197, 94), fill_color=(4, 22, 12, 250))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2

    # Battery Canister
    b_w = S * 0.32
    b_h = S * 0.52
    draw.rectangle([cx - b_w/2, cy - b_h/2, cx + b_w/2, cy + b_h/2], fill=(40, 60, 50), outline=(100, 180, 130), width=4)
    draw.rectangle([cx - b_w*0.2, cy - b_h/2 - S*0.06, cx + b_w*0.2, cy - b_h/2], fill=(120, 160, 140))

    # Glowing Lightning Bolt Core
    bolt_pts = [
        (cx + S*0.04, cy - S*0.2),
        (cx - S*0.14, cy + S*0.02),
        (cx - S*0.02, cy + S*0.02),
        (cx - S*0.06, cy + S*0.2),
        (cx + S*0.14, cy - S*0.02),
        (cx + S*0.02, cy - S*0.02)
    ]
    draw.polygon(bolt_pts, fill=(50, 255, 120), outline=(255, 255, 255), width=2)

    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def render_portrait_empty(target_size=128):
    """Tactical geodesic sector radar sweep with crosshairs."""
    S = 256
    img = create_base_card(S, border_color=(100, 116, 139), fill_color=(10, 15, 24, 250))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2

    # Radar concentric circles
    for r in [S*0.12, S*0.22, S*0.34]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(70, 90, 115, 180), width=2)

    # Radar Crosshairs
    draw.line([(cx - S*0.38, cy), (cx + S*0.38, cy)], fill=(100, 140, 180, 150), width=2)
    draw.line([(cx, cy - S*0.38), (cx, cy + S*0.38)], fill=(100, 140, 180, 150), width=2)

    # Geodesic Node Marker in center
    r0 = S * 0.06
    draw.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=(0, 229, 255), outline=(255, 255, 255), width=2)

    # 45-degree angle sweep beam
    sweep_pts = [(cx, cy), (cx + S*0.32, cy - S*0.28), (cx + S*0.38, cy - S*0.15)]
    draw.polygon(sweep_pts, fill=(0, 229, 255, 60))

    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

# Generate Portraits for Sector Intelligence Bay (128x128)
def generate_all():
    icons = {
        "icon_wall.png": render_icon_wall(64),
        "icon_harvester.png": render_icon_harvester(64),
        "icon_turret.png": render_icon_turret(64),
        "icon_assault.png": render_icon_assault(64),
        "icon_wave.png": render_icon_wave(64),
        "icon_base.png": render_icon_base(64),
        "icon_tech.png": render_icon_tech(64),
        "icon_energy.png": render_icon_energy(64),
    }
    for name, img in icons.items():
        p = os.path.join(ICONS_DIR, name)
        img.save(p, "PNG")
        print(f"Saved {p}")

    portraits = {
        "portrait_wall.png": render_icon_wall(128),
        "portrait_harvester.png": render_icon_harvester(128),
        "portrait_turret.png": render_icon_turret(128),
        "portrait_base.png": render_icon_base(128),
        "portrait_assault.png": render_icon_assault(128),
        "portrait_empty.png": render_portrait_empty(128),
    }
    for name, img in portraits.items():
        p = os.path.join(PORTRAITS_DIR, name)
        img.save(p, "PNG")
        print(f"Saved {p}")

if __name__ == "__main__":
    generate_all()

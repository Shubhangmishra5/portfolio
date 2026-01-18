from PIL import Image, ImageDraw, ImageFilter
import math

# Output settings
W, H = 1280, 720        # 16:9
NUM_FRAMES = 40
DURATION_MS = 80        # per frame
OUTPUT = "embedded_iot_hero.gif"

# Colors
BG = (2, 6, 23)         # deep navy
CYAN = (56, 189, 248)   # #38bdf8
PURPLE = (168, 85, 247) # #a855f7

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

frames = []

for i in range(NUM_FRAMES):
    t = i / NUM_FRAMES
    pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t)
    pulse_soft = 0.4 + 0.6 * math.sin(2 * math.pi * t)

    # Base background
    base = Image.new("RGB", (W, H), BG)
    base = base.convert("RGBA")
    draw = ImageDraw.Draw(base)

    # Subtle horizontal gradient overlay
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad)
    for y in range(0, H, 4):
        alpha = int(25 + 15 * math.sin(2 * math.pi * (y / H + t)))
        line_color = lerp_color(CYAN, PURPLE, y / H)
        gdraw.line([(0, y), (W, y)], fill=line_color + (alpha,))
    base = Image.alpha_composite(base, grad)

    # Foreground elements
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fgd = ImageDraw.Draw(fg)

    # Central microchip outline
    chip_margin_x, chip_margin_y = 420, 170
    chip_width, chip_height = 440, 380
    x0, y0 = chip_margin_x, chip_margin_y
    x1, y1 = chip_margin_x + chip_width, chip_margin_y + chip_height
    radius = 40
    chip_box = [x0, y0, x1, y1]

    chip_color = lerp_color(CYAN, PURPLE, 0.3 + 0.2 * math.sin(2 * math.pi * t))
    try:
        fgd.rounded_rectangle(chip_box, radius=radius, outline=chip_color, width=3)
    except Exception:
        fgd.rectangle(chip_box, outline=chip_color, width=3)

    # Chip pins
    pin_len = 18
    pin_gap = 26

    # Top pins
    y_top = y0 - pin_len
    for px in range(int(x0 + radius / 2), int(x1 - radius / 2), pin_gap):
        fgd.line([(px, y0), (px, y_top)], fill=chip_color, width=2)

    # Bottom pins
    y_bottom = y1 + pin_len
    for px in range(int(x0 + radius / 2), int(x1 - radius / 2), pin_gap):
        fgd.line([(px, y1), (px, y_bottom)], fill=chip_color, width=2)

    # Left pins
    x_left = x0 - pin_len
    for py in range(int(y0 + radius / 2), int(y1 - radius / 2), pin_gap):
        fgd.line([(x0, py), (x_left, py)], fill=chip_color, width=2)

    # Right pins
    x_right = x1 + pin_len
    for py in range(int(y0 + radius / 2), int(y1 - radius / 2), pin_gap):
        fgd.line([(x1, py), (x_right, py)], fill=chip_color, width=2)

    # BLE-like icon (left)
    ble_center = (chip_margin_x - 130, chip_margin_y + 40)
    bx, by = ble_center
    ble_size = 60
    ble_color = CYAN
    fgd.line([(bx, by - ble_size // 2), (bx, by + ble_size // 2)], fill=ble_color, width=3)
    fgd.line([(bx, by), (bx + ble_size // 2, by - ble_size // 3)], fill=ble_color, width=3)
    fgd.line([(bx, by), (bx - ble_size // 2, by - ble_size // 3)], fill=ble_color, width=3)
    fgd.line([(bx, by), (bx + ble_size // 2, by + ble_size // 3)], fill=ble_color, width=3)
    fgd.line([(bx, by), (bx - ble_size // 2, by + ble_size // 3)], fill=ble_color, width=3)

    # Cloud icon (right)
    cloud_color = PURPLE
    cx, cy = chip_margin_x + chip_width + 140, chip_margin_y + 60
    cw, ch = 160, 70
    fgd.line([(cx - cw // 2, cy + ch // 4), (cx + cw // 2, cy + ch // 4)], fill=cloud_color, width=3)
    fgd.arc([cx - cw // 2, cy, cx - cw // 2 + cw // 3, cy + ch // 2], 90, 270, fill=cloud_color, width=3)
    fgd.arc([cx - cw // 6, cy - ch // 4, cx + cw // 6, cy + ch // 2], 0, 180, fill=cloud_color, width=3)
    fgd.arc([cx + cw // 6, cy, cx + cw // 2, cy + ch // 2], 270, 90, fill=cloud_color, width=3)

    # Waveform / HRV line under chip
    wf_y = chip_margin_y + chip_height + 80
    wf_left = chip_margin_x - 100
    wf_right = chip_margin_x + chip_width + 100
    wf_amp = 40
    wf_points = []
    phase = 2 * math.pi * t

    for x in range(wf_left, wf_right, 8):
        xn = (x - wf_left) / (wf_right - wf_left)
        y = wf_y + wf_amp * math.sin(6 * math.pi * xn + phase) * (0.6 + 0.4 * math.sin(2 * math.pi * t))
        wf_points.append((x, y))

    wf_color = lerp_color(CYAN, PURPLE, 0.5 + 0.5 * math.sin(2 * math.pi * t))
    fgd.line(wf_points, fill=wf_color, width=3)

    # Data dots along waveform
    num_dots = 8
    for k in range(num_dots):
        u = (t + k / num_dots) % 1.0
        x = wf_left + u * (wf_right - wf_left)
        xn = u
        y = wf_y + wf_amp * math.sin(6 * math.pi * xn + phase)
        dot_color = lerp_color(CYAN, PURPLE, u)
        rdot = 5
        fgd.ellipse((x - rdot, y - rdot, x + rdot, y + rdot), fill=dot_color)

    # Neural network nodes (bottom-right area)
    nn_base_x, nn_base_y = chip_margin_x + chip_width + 140, wf_y + 100
    node_radius = 8
    nn_color = lerp_color(CYAN, PURPLE, 0.5)
    layer_offsets = [(-40, -40), (0, 0), (40, 40)]
    nodes = []

    for li, (ox, oy) in enumerate(layer_offsets):
        for j in range(3):
            x = nn_base_x + ox + li * 40
            y = nn_base_y + oy + (j - 1) * 30
            nodes.append((x, y))

    # Connections with subtle animated alpha
    for (x1, y1) in nodes:
        for (x2, y2) in nodes:
            if x2 > x1 and abs(y2 - y1) <= 40:
                alpha = int(80 + 40 * math.sin(2 * math.pi * (t + (x1 + y1) / (W + H))))
                col = nn_color + (alpha,)
                ImageDraw.Draw(fg).line([(x1, y1), (x2, y2)], fill=col, width=2)

    # Nodes
    for (x, y) in nodes:
        glow_t = 0.5 + 0.5 * math.sin(2 * math.pi * t + (x + y) * 0.01)
        col = lerp_color(CYAN, PURPLE, glow_t)
        fgd.ellipse((x - node_radius, y - node_radius, x + node_radius, y + node_radius),
                    outline=col, width=2)

    # Inner chip traces
    trace_color = lerp_color(CYAN, PURPLE, 0.2 + 0.3 * pulse)
    tx0, ty0, tx1, ty1 = x0 + 40, y0 + 40, x1 - 40, y1 - 40
    for n in range(5):
        yy = ty0 + n * (ty1 - ty0) / 4
        offset = 10 * math.sin(2 * math.pi * t + n)
        fgd.line([(tx0, yy), (tx1 - 80 + offset, yy)], fill=trace_color, width=2)
        fgd.line([(tx1 - 80 + offset, yy), (tx1 - 40, yy - 10)], fill=trace_color, width=2)

    # Glow layer
    glow = fg.filter(ImageFilter.GaussianBlur(radius=16))
    glow_mask = glow.split()[-1].point(lambda a: int(a * (0.6 + 0.4 * pulse_soft)))

    base = Image.composite(glow, base, glow_mask)
    base = Image.alpha_composite(base, fg)

    frames.append(base)

# Save as GIF (Pillow handles palette conversion)
frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=DURATION_MS,
    loop=0,
    disposal=2,
)

print(f"Saved {OUTPUT}")

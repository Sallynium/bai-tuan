# -*- coding: utf-8 -*-
"""把 Gemini 生成的 3x3 白底 sprite sheet 去背、正規化成標準九宮格。

用法: python tools/build-sprites.py <來源圖> <輸出圖> [BG_MIN]
BG_MIN: 背景判定閾值,預設 205。淺色狗(薩摩耶)描邊接近白色時要拉高(如 238),
        避免 flood fill 從描邊漏進去吃掉狗身。
輸出: 3x3、每格 CELL_W x CELL_H、透明背景、姿勢腳底貼齊格子底部。
"""
import sys
import collections
from PIL import Image

CELL_W, CELL_H = 300, 260
PAD = 6          # 格內留白
MIN_AREA = 4000  # 小於此面積的雜點(星星等)不算姿勢


def main(src, dst, bg_min=205):
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()

    def is_bg(p):
        r, g, b, a = p
        return a < 10 or (r > bg_min and g > bg_min and b > bg_min)

    # 1) 從四邊 flood fill 出背景遮罩(奶油白胸口被輪廓線包住,不會被吞)
    bg = bytearray(w * h)
    dq = collections.deque()
    for x in range(w):
        for y in (0, h - 1):
            if is_bg(px[x, y]) and not bg[y * w + x]:
                bg[y * w + x] = 1
                dq.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(px[x, y]) and not bg[y * w + x]:
                bg[y * w + x] = 1
                dq.append((x, y))
    while dq:
        x, y = dq.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not bg[ny * w + nx] and is_bg(px[nx, ny]):
                bg[ny * w + nx] = 1
                dq.append((nx, ny))

    # 2) 背景設為全透明;貼著背景的淺色邊緣做半透明,避免白邊
    for y in range(h):
        for x in range(w):
            i = y * w + x
            r, g, b, a = px[x, y]
            if bg[i]:
                px[x, y] = (r, g, b, 0)
                continue
            near_bg = ((x > 0 and bg[i - 1]) or (x < w - 1 and bg[i + 1]) or
                       (y > 0 and bg[i - w]) or (y < h - 1 and bg[i + w]))
            if near_bg:
                avg = (r + g + b) / 3
                full_at, zero_at = bg_min - 25, bg_min + 30
                if avg > full_at:
                    alpha = int(max(0, min(255, 255 * (zero_at - avg) / (zero_at - full_at))))
                    px[x, y] = (r, g, b, alpha)

    # 3) 連通元件找出各姿勢
    seen = bytearray(w * h)
    blobs = []
    for y0 in range(h):
        for x0 in range(w):
            i0 = y0 * w + x0
            if bg[i0] or seen[i0]:
                continue
            q = collections.deque([(x0, y0)])
            seen[i0] = 1
            minx, miny, maxx, maxy, area = x0, y0, x0, y0, 0
            while q:
                x, y = q.popleft()
                area += 1
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    ni = ny * w + nx
                    if 0 <= nx < w and 0 <= ny < h and not bg[ni] and not seen[ni]:
                        seen[ni] = 1
                        q.append((nx, ny))
            if area >= MIN_AREA:
                blobs.append({"box": (minx, miny, maxx + 1, maxy + 1),
                              "cx": (minx + maxx) / 2, "cy": (miny + maxy) / 2,
                              "area": area})

    if len(blobs) != 9:
        print("WARN: 找到 %d 個姿勢塊(預期 9),bbox:" % len(blobs))
        for b in blobs:
            print("  ", b["box"], "area", b["area"])
        if len(blobs) < 9:
            sys.exit(1)

    # 4) 依 y 分三列、列內依 x 排序
    blobs.sort(key=lambda b: b["cy"])
    rows = [sorted(blobs[i:i + 3], key=lambda b: b["cx"]) for i in range(0, 9, 3)]

    # 5) 貼進標準格:等比縮到格內、水平置中、腳底貼齊格底
    sheet = Image.new("RGBA", (CELL_W * 3, CELL_H * 3), (0, 0, 0, 0))
    for r, row in enumerate(rows):
        for c, b in enumerate(row):
            crop = im.crop(b["box"])
            bw, bh = crop.size
            scale = min((CELL_W - PAD * 2) / bw, (CELL_H - PAD * 2) / bh, 1.0)
            if scale < 1.0:
                crop = crop.resize((max(1, int(bw * scale)), max(1, int(bh * scale))),
                                   Image.LANCZOS)
            bw, bh = crop.size
            ox = c * CELL_W + (CELL_W - bw) // 2
            oy = r * CELL_H + (CELL_H - PAD - bh)
            sheet.alpha_composite(crop, (ox, oy))

    sheet.save(dst, optimize=True)
    q = sheet.quantize(colors=128, method=Image.Quantize.FASTOCTREE)
    q.save(dst + ".q.png", optimize=True)
    import os
    print("OK 9 poses -> %s" % dst)
    print("RGBA: %d bytes / 量化128色: %d bytes" % (os.path.getsize(dst),
                                                    os.path.getsize(dst + ".q.png")))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 205)

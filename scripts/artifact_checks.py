#!/usr/bin/env python3
"""Small, dependency-free artifact checks shared by package validators."""

from __future__ import annotations

import hashlib
import math
import re
import struct
import unicodedata
import zlib
from pathlib import Path
from xml.etree import ElementTree


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
GIF_SIGNATURES = {b"GIF87a", b"GIF89a"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read PNG {path}: {exc}") from exc
    if len(data) < 57 or data[:8] != PNG_SIGNATURE:
        raise ValueError(f"not a complete PNG: {path}")
    if len(data) > 64 * 1024 * 1024:
        raise ValueError(f"PNG exceeds the 64 MiB evidence limit: {path}")

    offset = 8
    ihdr: bytes | None = None
    idat: list[bytes] = []
    has_iend = False
    has_palette = False
    first_chunk = True
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError(f"truncated PNG chunk in {path}")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(data):
            raise ValueError(f"truncated PNG payload in {path}")
        payload = data[offset + 8:offset + 8 + length]
        recorded_crc = struct.unpack(">I", data[offset + 8 + length:end])[0]
        actual_crc = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
        if recorded_crc != actual_crc:
            raise ValueError(f"PNG chunk CRC mismatch in {path}")
        if first_chunk and (chunk_type != b"IHDR" or length != 13):
            raise ValueError(f"PNG must begin with a 13-byte IHDR chunk: {path}")
        first_chunk = False
        if chunk_type == b"IHDR":
            if ihdr is not None: raise ValueError(f"PNG contains multiple IHDR chunks: {path}")
            ihdr = payload
        elif chunk_type == b"PLTE":
            has_palette = True
        elif chunk_type == b"IDAT":
            idat.append(payload)
        elif chunk_type == b"IEND":
            if length != 0 or end != len(data): raise ValueError(f"PNG IEND must be empty and final: {path}")
            has_iend = True
            offset = end
            break
        offset = end

    if ihdr is None or not idat or not has_iend:
        raise ValueError(f"PNG requires IHDR, IDAT, and IEND chunks: {path}")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", ihdr)
    if not width or not height or width * height > 20_000_000:
        raise ValueError(f"PNG dimensions are empty or exceed the evidence limit: {path}")
    valid_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
    if color_type not in valid_depths or bit_depth not in valid_depths[color_type]:
        raise ValueError(f"unsupported PNG color type or bit depth: {path}")
    if color_type == 3 and not has_palette:
        raise ValueError(f"indexed PNG is missing PLTE: {path}")
    if compression != 0 or filter_method != 0 or interlace != 0:
        raise ValueError(f"PNG evidence must use standard compression/filtering and no interlace: {path}")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    row_bytes = (width * channels * bit_depth + 7) // 8
    expected_size = height * (row_bytes + 1)
    inflater = zlib.decompressobj()
    try:
        decoded = inflater.decompress(b"".join(idat), expected_size + 1)
    except zlib.error as exc:
        raise ValueError(f"PNG IDAT cannot be decoded in {path}: {exc}") from exc
    if len(decoded) != expected_size or not inflater.eof or inflater.unconsumed_tail:
        raise ValueError(f"PNG decoded payload is truncated or oversized: {path}")
    for row in range(height):
        if decoded[row * (row_bytes + 1)] > 4:
            raise ValueError(f"PNG contains an invalid row filter: {path}")
    return width, height


def gif_metadata(path: Path, *, validate_lzw: bool = True) -> tuple[int, int, int, int]:
    """Return width, height, frame count, and duration in milliseconds."""
    try:
        file_size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"cannot stat GIF {path}: {exc}") from exc
    if file_size > 16 * 1024 * 1024:
        raise ValueError(f"GIF exceeds the 16 MiB README limit: {path}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read GIF {path}: {exc}") from exc
    if len(data) < 14 or data[:6] not in GIF_SIGNATURES:
        raise ValueError(f"not a complete GIF: {path}")
    if len(data) != file_size:
        raise ValueError(f"GIF size changed while reading: {path}")

    width, height = struct.unpack("<HH", data[6:10])
    if not width or not height or width * height > 2_000_000:
        raise ValueError(f"GIF dimensions are empty or exceed the README limit: {path}")
    offset = 13
    packed = data[10]
    global_palette_entries = 0
    if packed & 0x80:
        global_palette_entries = 2 ** ((packed & 0x07) + 1)
        offset += 3 * global_palette_entries
    if offset > len(data):
        raise ValueError(f"truncated GIF color table in {path}")

    def sub_blocks() -> list[bytes]:
        nonlocal offset
        blocks: list[bytes] = []
        while True:
            if offset >= len(data):
                raise ValueError(f"truncated GIF data blocks in {path}")
            size = data[offset]
            offset += 1
            if size == 0:
                return blocks
            end = offset + size
            if end > len(data):
                raise ValueError(f"truncated GIF data block in {path}")
            blocks.append(data[offset:end])
            offset = end

    frame_count = 0
    duration_ms = 0
    pending_delay_cs = 0
    found_trailer = False
    while offset < len(data):
        introducer = data[offset]
        offset += 1
        if introducer == 0x3B:
            if offset != len(data):
                raise ValueError(f"GIF trailer must be final in {path}")
            found_trailer = True
            break
        if introducer == 0x21:
            if offset >= len(data):
                raise ValueError(f"truncated GIF extension in {path}")
            label = data[offset]
            offset += 1
            blocks = sub_blocks()
            if label == 0xF9:
                if len(blocks) != 1 or len(blocks[0]) != 4:
                    raise ValueError(f"invalid GIF graphics control extension in {path}")
                pending_delay_cs = struct.unpack("<H", blocks[0][1:3])[0]
            continue
        if introducer == 0x2C:
            end = offset + 9
            if end > len(data):
                raise ValueError(f"truncated GIF image descriptor in {path}")
            descriptor = data[offset:end]
            offset = end
            left, top, frame_width, frame_height = struct.unpack("<HHHH", descriptor[:8])
            if not frame_width or not frame_height or left + frame_width > width or top + frame_height > height:
                raise ValueError(f"GIF frame rectangle exceeds the logical screen in {path}")
            palette_entries = global_palette_entries
            if descriptor[8] & 0x80:
                palette_entries = 2 ** ((descriptor[8] & 0x07) + 1)
                offset += 3 * palette_entries
            if palette_entries == 0:
                raise ValueError(f"GIF frame has no active color table in {path}")
            if offset >= len(data):
                raise ValueError(f"truncated GIF image data in {path}")
            minimum_code_size = data[offset]
            offset += 1
            if not 2 <= minimum_code_size <= 8:
                raise ValueError(f"GIF LZW minimum code size must be 2 to 8 in {path}")
            image_blocks = sub_blocks()
            if not image_blocks:
                raise ValueError(f"GIF image data cannot be empty in {path}")
            if validate_lzw:
                _validate_gif_lzw(
                    b"".join(image_blocks),
                    minimum_code_size,
                    frame_width * frame_height,
                    palette_entries,
                    path,
                )
            frame_count += 1
            if frame_count > 300:
                raise ValueError(f"GIF exceeds the 300-frame README limit: {path}")
            duration_ms += pending_delay_cs * 10
            pending_delay_cs = 0
            continue
        raise ValueError(f"unsupported GIF block 0x{introducer:02x} in {path}")

    if not found_trailer or frame_count == 0:
        raise ValueError(f"GIF requires image frames and a final trailer: {path}")
    return width, height, frame_count, duration_ms


def _validate_gif_lzw(
    compressed: bytes,
    minimum_code_size: int,
    expected_pixels: int,
    palette_entries: int,
    path: Path,
) -> None:
    """Decode one GIF image stream and prove it yields exactly its pixel rectangle."""
    clear_code = 1 << minimum_code_size
    end_code = clear_code + 1
    code_size = minimum_code_size + 1
    next_code = end_code + 1
    # Dictionary entries are (first palette index, decoded length, maximum palette index).
    # Tracking metadata instead of materializing strings keeps validation bounded.
    dictionary: dict[int, tuple[int, int, int]] = {index: (index, 1, index) for index in range(clear_code)}
    byte_offset = 0
    bit_buffer = 0
    buffered_bits = 0
    decoded_pixels = 0
    previous: tuple[int, int, int] | None = None
    saw_clear = False
    saw_end = False

    def reset_dictionary() -> None:
        nonlocal dictionary, code_size, next_code, previous
        dictionary = {index: (index, 1, index) for index in range(clear_code)}
        code_size = minimum_code_size + 1
        next_code = end_code + 1
        previous = None

    while True:
        while buffered_bits < code_size and byte_offset < len(compressed):
            bit_buffer |= compressed[byte_offset] << buffered_bits
            buffered_bits += 8
            byte_offset += 1
        if buffered_bits < code_size:
            break
        code = bit_buffer & ((1 << code_size) - 1)
        bit_buffer >>= code_size
        buffered_bits -= code_size

        if code == clear_code:
            saw_clear = True
            reset_dictionary()
            continue
        if not saw_clear:
            raise ValueError(f"GIF LZW stream must begin with a clear code in {path}")
        if code == end_code:
            saw_end = True
            break

        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code and previous is not None:
            entry = (previous[0], previous[1] + 1, previous[2])
        else:
            raise ValueError(f"GIF LZW stream contains an invalid code in {path}")

        if entry[2] >= palette_entries:
            raise ValueError(f"GIF pixel index exceeds its active color table in {path}")
        decoded_pixels += entry[1]
        if decoded_pixels > expected_pixels:
            raise ValueError(f"GIF LZW stream decodes beyond its frame rectangle in {path}")

        if previous is not None and next_code < 4096:
            dictionary[next_code] = (previous[0], previous[1] + 1, max(previous[2], entry[0]))
            next_code += 1
            if next_code == (1 << code_size) and code_size < 12:
                code_size += 1
        previous = entry

    if not saw_end:
        raise ValueError(f"GIF LZW stream is missing an end code in {path}")
    if decoded_pixels != expected_pixels:
        raise ValueError(f"GIF LZW stream does not fill its frame rectangle in {path}")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _numeric_attribute(node: ElementTree.Element, name: str, path: Path) -> float:
    raw = node.attrib.get(name)
    if raw is None:
        raise ValueError(f"SVG text requires numeric {name}: {path}")
    try:
        value = float(raw.replace("px", ""))
    except ValueError as exc:
        raise ValueError(f"SVG text requires numeric {name}: {path}") from exc
    if not math.isfinite(value):
        raise ValueError(f"SVG text requires finite {name}: {path}")
    return value


def validate_svg_safety(path: Path, *, allow_local_png: bool = False) -> ElementTree.Element:
    try:
        raw = path.read_text(encoding="utf-8")
        lowered = raw.lower()
        if "<?xml-stylesheet" in lowered or "<!doctype" in lowered or "<!entity" in lowered:
            raise ValueError(f"SVG forbids stylesheets, doctypes, and entities: {path}")
        root = ElementTree.fromstring(raw)
    except (ElementTree.ParseError, OSError) as exc:
        raise ValueError(f"cannot parse SVG {path}: {exc}") from exc

    if _local_name(root.tag) != "svg":
        raise ValueError(f"review evidence root element must be <svg>: {path}")

    blocked_elements = {
        "a", "animate", "animateMotion", "animateTransform", "discard", "foreignObject", "iframe",
        "script", "set", "style", "use",
    }
    for node in root.iter():
        name = _local_name(node.tag)
        if name == "image":
            if not allow_local_png:
                raise ValueError(f"SVG review evidence forbids <image>: {path}")
            allowed_image_attributes = {"height", "href", "opacity", "preserveAspectRatio", "width", "x", "y"}
            unknown_image_attributes = {_local_name(attribute) for attribute in node.attrib} - allowed_image_attributes
            if unknown_image_attributes:
                raise ValueError(f"SVG local image has unsupported attributes {sorted(unknown_image_attributes)}: {path}")
            href = next((value for attribute, value in node.attrib.items() if _local_name(attribute) == "href"), "")
            if not href or Path(href).name != href or Path(href).suffix.lower() != ".png":
                raise ValueError(f"SVG local image must reference a sibling PNG filename: {path}")
            linked_png = path.parent / href
            if not linked_png.is_file():
                raise ValueError(f"SVG local image does not exist: {linked_png}")
            if png_dimensions(linked_png) not in {(720, 1280), (1080, 1920)}:
                raise ValueError(f"SVG local image must be a native 9:16 review asset: {linked_png}")
        if name in blocked_elements:
            raise ValueError(f"SVG review evidence forbids <{name}>: {path}")
        forbidden_attributes = {"class", "style"}.intersection(node.attrib)
        if forbidden_attributes:
            raise ValueError(f"SVG review evidence forbids CSS hooks {sorted(forbidden_attributes)}: {path}")
        for attribute, value in node.attrib.items():
            attribute_name = _local_name(attribute).lower()
            if attribute_name.startswith("on"):
                raise ValueError(f"SVG review evidence forbids event attributes: {path}")
            if name != "image" and attribute_name in {"href", "base"} and not value.startswith("#"):
                raise ValueError(f"SVG review evidence forbids external references: {path}")
            for match in re.finditer(r"url\(([^)]*)\)", value, re.IGNORECASE):
                target = match.group(1).strip().strip("\"'")
                if not target.startswith("#"):
                    raise ValueError(f"SVG review evidence forbids external URL references: {path}")
    return root


def _estimated_text_width(value: str, size: float, letter_spacing: float) -> float:
    units = 0.0
    for character in value:
        if character.isspace():
            units += 0.35
        elif unicodedata.east_asian_width(character) in {"W", "F"}:
            units += 1.0
        elif unicodedata.category(character).startswith("P"):
            units += 0.48
        else:
            units += 0.62
    return units * size + max(0, len(value) - 1) * max(0.0, letter_spacing)


def svg_viewbox_and_flat_text(path: Path) -> tuple[tuple[float, float, float, float], list[tuple[str, float, float, float, float]]]:
    root = validate_svg_safety(path, allow_local_png=True)

    raw_viewbox = root.attrib.get("viewBox", "")
    try:
        viewbox = tuple(float(part) for part in raw_viewbox.replace(",", " ").split())
    except ValueError as exc:
        raise ValueError(f"invalid SVG viewBox in {path}: {raw_viewbox!r}") from exc
    if len(viewbox) != 4:
        raise ValueError(f"SVG viewBox must contain four numbers: {path}")
    if not all(math.isfinite(value) for value in viewbox) or viewbox[2] <= 0 or viewbox[3] <= 0:
        raise ValueError(f"SVG viewBox must contain finite positive dimensions: {path}")
    try:
        declared_width = float(root.attrib.get("width", "nan").replace("px", ""))
        declared_height = float(root.attrib.get("height", "nan").replace("px", ""))
    except ValueError as exc:
        raise ValueError(f"SVG root requires numeric width and height: {path}") from exc
    if not math.isfinite(declared_width) or not math.isfinite(declared_height) or declared_width != viewbox[2] or declared_height != viewbox[3]:
        raise ValueError(f"SVG root width and height must match its viewBox: {path}")
    root_forbidden = {"transform", "filter", "mask", "clip-path"}.intersection(root.attrib)
    if root_forbidden:
        raise ValueError(f"SVG root cannot transform or clip review evidence: {sorted(root_forbidden)} in {path}")
    if root.attrib.get("display") == "none" or root.attrib.get("visibility") in {"hidden", "collapse"}:
        raise ValueError(f"hidden SVG root is not valid evidence: {path}")
    try:
        root_opacity = float(root.attrib.get("opacity", "1"))
        root_fill_opacity = float(root.attrib.get("fill-opacity", "1"))
        if not math.isfinite(root_opacity) or not math.isfinite(root_fill_opacity) or root_opacity <= 0 or root_fill_opacity <= 0:
            raise ValueError(f"transparent SVG root is not valid evidence: {path}")
    except ValueError as exc:
        if "transparent SVG root" in str(exc): raise
        raise ValueError(f"invalid SVG root opacity in {path}") from exc

    visible_text: list[tuple[str, float, float, float, float]] = []
    for child in root:
        if _local_name(child.tag) != "text":
            continue
        forbidden = {"class", "style", "transform", "filter", "mask", "clip-path"}.intersection(child.attrib)
        if forbidden:
            raise ValueError(f"required SVG text must be flat and attribute-styled; forbidden {sorted(forbidden)} in {path}")
        allowed_text_attributes = {"fill", "fill-opacity", "font-family", "font-size", "font-style", "font-weight", "letter-spacing", "opacity", "x", "y"}
        unknown_text_attributes = set(child.attrib) - allowed_text_attributes
        if unknown_text_attributes:
            raise ValueError(f"SVG review text contains unsupported attributes {sorted(unknown_text_attributes)}: {path}")
        if list(child):
            raise ValueError(f"SVG review text cannot contain tspan or nested elements: {path}")
        if child.attrib.get("display") == "none" or child.attrib.get("visibility") in {"hidden", "collapse"}:
            raise ValueError(f"hidden SVG text is not valid evidence: {path}")
        fill = child.attrib.get("fill")
        if fill is None or not re.fullmatch(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?", fill.strip()):
            raise ValueError(f"SVG text requires an explicit opaque hex fill: {path}")
        try:
            opacity = float(child.attrib.get("opacity", "1"))
            fill_opacity = float(child.attrib.get("fill-opacity", "1"))
        except ValueError as exc:
            raise ValueError(f"invalid text opacity in {path}") from exc
        if not math.isfinite(opacity) or not math.isfinite(fill_opacity) or opacity <= 0 or fill_opacity <= 0:
            raise ValueError(f"transparent SVG text is not valid evidence: {path}")
        x = _numeric_attribute(child, "x", path)
        y = _numeric_attribute(child, "y", path)
        x0, y0, width, height = viewbox
        if not x0 <= x <= x0 + width or not y0 <= y <= y0 + height:
            raise ValueError(f"off-canvas SVG text is not valid evidence: {path}")
        size = _numeric_attribute(child, "font-size", path)
        value = (child.text or "").strip()
        if value:
            raw_spacing = child.attrib.get("letter-spacing", "0").replace("px", "")
            try:
                letter_spacing = float(raw_spacing)
            except ValueError as exc:
                raise ValueError(f"SVG text requires numeric letter-spacing: {path}") from exc
            if not math.isfinite(letter_spacing):
                raise ValueError(f"SVG text requires finite letter-spacing: {path}")
            visible_text.append((value, size, x, y, _estimated_text_width(value, size, letter_spacing)))

    nested_text = [node for node in root.iter() if _local_name(node.tag) == "text"]
    if len(nested_text) != len(visible_text):
        raise ValueError(f"all review text must be direct children of the SVG root: {path}")
    return viewbox, visible_text


def sha256_static_artifact(path: Path) -> str:
    """Hash the SVG plus every validated sibling PNG it references."""
    root = validate_svg_safety(path, allow_local_png=True)
    digest = hashlib.sha256()
    digest.update(b"inkbrush-static-artifact-v1\0")
    digest.update(path.name.encode("utf-8"))
    digest.update(b"\0")
    digest.update(path.read_bytes())
    for node in root.iter():
        if _local_name(node.tag) != "image":
            continue
        href = next(value for attribute, value in node.attrib.items() if _local_name(attribute) == "href")
        digest.update(b"\0linked-png\0")
        digest.update(href.encode("utf-8"))
        digest.update(b"\0")
        digest.update((path.parent / href).read_bytes())
    return digest.hexdigest()

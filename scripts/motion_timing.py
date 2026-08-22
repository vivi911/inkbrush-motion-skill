#!/usr/bin/env python3
"""Load and verify the one timing contract shared by web, GIF, and QA."""

from __future__ import annotations

import json
import math
from pathlib import Path


PREFIX = "window.INKBRUSH_TIMING = "
TOP_LEVEL_FIELDS = {
    "durationMs", "fps", "breaks", "strokeSegments", "actionProgress",
    "knowledgeThresholds", "inkDelays", "inkContact", "gif", "deadlines",
}


def load_motion_timing(path: Path) -> dict:
    source = path.read_text(encoding="utf-8")
    if not source.startswith(PREFIX) or not source.endswith(";\n"):
        raise ValueError("motion-timing.js must contain one canonical JSON assignment")
    try:
        timing = json.loads(source[len(PREFIX):-2])
    except json.JSONDecodeError as exc:
        raise ValueError(f"motion-timing.js contains invalid JSON: {exc}") from exc
    if not isinstance(timing, dict):
        raise ValueError("motion-timing.js timing payload must be an object")
    return timing


def _number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def stroke_progress(progress: float, timing: dict) -> float:
    segments = timing["strokeSegments"]
    if progress < segments[0][0]:
        return 0.0
    for start, end, source, target in segments:
        if progress < end:
            return source + (target - source) * ease((progress - start) / (end - start))
    return 1.0


def progress_for_stroke(target: float, timing: dict) -> float:
    low, high = 0.0, 1.0
    for _ in range(64):
        middle = (low + high) / 2
        if stroke_progress(middle, timing) < target:
            low = middle
        else:
            high = middle
    return high


def preview_metrics(timing: dict) -> dict[str, float]:
    duration_ms = timing["durationMs"]
    breaks = timing["breaks"]
    context = timing["knowledgeThresholds"]["context"]
    gif = timing["gif"]
    samples = gif["timelineSamples"]
    active_last = gif["activeLastIndex"]
    sample_ms = gif["frameDurationMs"]

    def first_sample(predicate) -> float:
        for index in range(samples):
            progress = min(1.0, index / active_last)
            if predicate(progress):
                return index * sample_ms
        return math.inf

    return {
        "webFirstInkMs": breaks[0] * duration_ms,
        "webFirstThreeMs": breaks[2] * duration_ms,
        "webContextMs": progress_for_stroke(context, timing) * duration_ms,
        "gifFirstInkMs": first_sample(lambda progress: stroke_progress(progress, timing) > 0),
        "gifFirstThreeMs": first_sample(lambda progress: progress >= breaks[2]),
        "gifContextMs": first_sample(lambda progress: stroke_progress(progress, timing) >= context),
        "gifFinalHoldMs": (samples - active_last) * sample_ms,
        "gifDurationMs": samples * sample_ms,
    }


def minimum_final_hold_frames(timing: dict) -> int:
    return math.ceil(timing["deadlines"]["finalHoldMinMs"] * timing["fps"] / 1000)


def validate_motion_timing(timing: dict) -> list[str]:
    errors: list[str] = []
    if set(timing) != TOP_LEVEL_FIELDS:
        errors.append("motion timing top-level fields drift")
        return errors

    duration_ms, fps = timing.get("durationMs"), timing.get("fps")
    if not _number(duration_ms) or duration_ms <= 0: errors.append("motion timing durationMs must be positive")
    if not isinstance(fps, int) or isinstance(fps, bool) or fps <= 0: errors.append("motion timing fps must be a positive integer")

    breaks = timing.get("breaks")
    segments = timing.get("strokeSegments")
    actions = timing.get("actionProgress")
    if not isinstance(breaks, list) or len(breaks) != 8 or not all(_number(value) for value in breaks) or breaks != sorted(breaks) or not 0 < breaks[0] < breaks[-1] < 1:
        errors.append("motion timing breaks must contain eight increasing fractions")
    if not isinstance(segments, list) or len(segments) != 7 or any(not isinstance(row, list) or len(row) != 4 or not all(_number(value) for value in row) for row in segments):
        errors.append("motion timing strokeSegments must contain seven numeric rows")
    elif isinstance(breaks, list) and len(breaks) == 8:
        boundaries = [segments[0][0], *[row[1] for row in segments]]
        if boundaries != breaks or segments[0][2] != 0 or segments[-1][3] != 1:
            errors.append("motion timing stroke segments must exactly span the action breaks")
        for previous, current in zip(segments, segments[1:]):
            if previous[1] != current[0] or previous[3] != current[2]:
                errors.append("motion timing stroke segments must be continuous")
                break
    if not isinstance(actions, list) or len(actions) != 9 or not all(_number(value) for value in actions) or actions != sorted(actions) or actions[-1] != 1:
        errors.append("motion timing actionProgress must contain nine ordered samples")

    knowledge = timing.get("knowledgeThresholds")
    if not isinstance(knowledge, dict) or set(knowledge) != {"context", "action", "evidence", "result"} or not all(_number(value) for value in knowledge.values()):
        errors.append("motion timing knowledge thresholds are invalid")
    elif list(knowledge.values()) != sorted(knowledge.values()) or not 0 < knowledge["context"] < knowledge["result"] < 1:
        errors.append("motion timing knowledge thresholds must be increasing fractions")

    ink_delays = timing.get("inkDelays")
    if not isinstance(ink_delays, dict) or set(ink_delays) != {"diffusionFrames", "dryingFrames"}:
        errors.append("motion timing ink delays are invalid")
    elif any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in ink_delays.values()) or ink_delays["diffusionFrames"] >= ink_delays["dryingFrames"]:
        errors.append("motion timing ink delays must be increasing positive frame counts")

    ink_contact = timing.get("inkContact")
    if not isinstance(ink_contact, dict) or set(ink_contact) != {"activeCoreMaxPixels"}:
        errors.append("motion timing ink contact fields are invalid")
    else:
        active_core = ink_contact["activeCoreMaxPixels"]
        if not _number(active_core) or not 4 <= active_core <= 18:
            errors.append("active ink core must stay within 4-18 pixels at the brush tip")

    gif = timing.get("gif")
    if not isinstance(gif, dict) or set(gif) != {"width", "height", "timelineSamples", "activeLastIndex", "frameDurationMs"}:
        errors.append("motion timing GIF fields are invalid")
    elif any(not isinstance(gif[key], int) or isinstance(gif[key], bool) or gif[key] <= 0 for key in gif):
        errors.append("motion timing GIF values must be positive integers")
    elif gif["width"] * 16 != gif["height"] * 9 or gif["activeLastIndex"] >= gif["timelineSamples"]:
        errors.append("motion timing GIF dimensions or sample bounds are invalid")

    deadlines = timing.get("deadlines")
    deadline_fields = {"firstInkMaxMs", "firstThreeMinMs", "firstThreeMaxMs", "contextMaxMs", "finalHoldMinMs"}
    if not isinstance(deadlines, dict) or set(deadlines) != deadline_fields or not all(_number(value) and value > 0 for value in deadlines.values()):
        errors.append("motion timing deadlines are invalid")
    elif deadlines["firstThreeMinMs"] > deadlines["firstThreeMaxMs"]:
        errors.append("motion timing first-three deadline range is inverted")

    if errors:
        return errors
    metrics = preview_metrics(timing)
    if metrics["webFirstInkMs"] > deadlines["firstInkMaxMs"] or metrics["gifFirstInkMs"] > deadlines["firstInkMaxMs"]:
        errors.append("first visible ink misses the public-preview deadline")
    if not deadlines["firstThreeMinMs"] <= metrics["webFirstThreeMs"] <= deadlines["firstThreeMaxMs"]:
        errors.append("web hover-touch-press timing misses its deadline range")
    if not deadlines["firstThreeMinMs"] <= metrics["gifFirstThreeMs"] <= deadlines["firstThreeMaxMs"]:
        errors.append("GIF hover-touch-press timing misses its deadline range")
    if metrics["webContextMs"] > deadlines["contextMaxMs"] or metrics["gifContextMs"] > deadlines["contextMaxMs"]:
        errors.append("Context reveal misses the public-preview deadline")
    if metrics["gifFinalHoldMs"] < deadlines["finalHoldMinMs"]:
        errors.append("GIF final hold misses the public-preview deadline")
    return errors

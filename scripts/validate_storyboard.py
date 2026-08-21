#!/usr/bin/env python3
"""Validate InkBrush Motion storyboard state and supplied artifact evidence."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from artifact_checks import png_dimensions, sha256_file, sha256_static_artifact, svg_viewbox_and_flat_text
from motion_timing import load_motion_timing, minimum_final_hold_frames


STATES = {"PLAN_ONLY", "STATIC_REVIEW_READY", "MOTION_PROOF_READY", "RENDERER_REQUIRED", "HOLD"}
STATIC_STATES = {"STATIC_REVIEW_READY", "MOTION_PROOF_READY", "RENDERER_REQUIRED"}
STYLE_RECIPES = {"shan-shui-scroll", "minimal-calligraphy", "seal-diagram"}
BRUSH_MODES = {"none", "brush-only", "real-hand-nine-action"}
RENDERER_LANES = {"svg-js", "gsap-svg", "remotion-svg", "after-effects"}
NINE_ACTIONS = ["hover", "touch", "press", "travel", "turn", "lift", "return", "finish", "leave"]
HEX64 = re.compile(r"^[a-f0-9]{64}$")
REQUIRED_FIELDS = {
    "version", "status", "title", "summary", "aspectRatio", "width", "height", "fps",
    "previewSeconds", "finalHoldFrames", "safeMarginPercent", "styleRecipe", "textMode", "brushMode", "beats",
}
TOP_LEVEL_FIELDS = REQUIRED_FIELDS | {"$schema", "realHandProfile", "staticArtifact", "staticArtifactSha256", "motionEvidence"}
BEAT_FIELDS = {"id", "label", "copy", "zhLabel", "startSecond", "endSecond"}
REAL_HAND_FIELDS = {"profile", "brushAngleRange", "armEntry", "cropBoundary", "sleeveStyle", "actions", "inkPhysics"}
INK_PHYSICS_FIELDS = {
    "paper", "freshCoreOpacity", "wetEdgeOpacity", "dryTrailOpacity", "dryBrushGapPercent",
    "dryingDelayFrames", "diffusionDelayFrames",
}
MOTION_FIELDS = {
    "rendererLane", "rendererOwner", "reviewer", "staticApprovalSha256", "frames",
    "nineActionProof", "nineActionProofSha256",
}
FRAME_FIELDS = {"role", "frame", "path", "sha256"}


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _reject_json_constant(token: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {token}")


def _artifact(root: Path, raw_path: Any, field: str, errors: list[str]) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        errors.append(f"{field} must be a non-empty package-relative path")
        return None
    path = (root / raw_path).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{field} escapes the package root")
        return None
    if not path.is_file():
        errors.append(f"{field} does not exist: {raw_path}")
        return None
    return path


def validate(plan: dict[str, Any], base_dir: Path | None) -> list[str]:
    if not isinstance(plan, dict):
        return ["storyboard plan must be a JSON object"]
    errors: list[str] = []
    try:
        timing = load_motion_timing(Path(__file__).resolve().parents[1] / "motion-timing.js")
        min_final_hold_frames = minimum_final_hold_frames(timing)
    except (OSError, ValueError) as exc:
        errors.append(f"motion timing contract cannot be loaded: {exc}")
        min_final_hold_frames = None
    missing = sorted(REQUIRED_FIELDS - plan.keys())
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
    unknown = sorted(plan.keys() - TOP_LEVEL_FIELDS)
    if unknown:
        errors.append(f"unknown top-level fields: {', '.join(unknown)}")

    status = plan.get("status")
    if plan.get("version") != "1.0": errors.append("version must be 1.0")
    if status not in STATES: errors.append(f"status must be one of {sorted(STATES)}")
    if not isinstance(plan.get("title"), str) or not plan.get("title", "").strip(): errors.append("title must be non-empty")
    if not isinstance(plan.get("summary"), str) or not plan.get("summary", "").strip(): errors.append("summary must be non-empty")
    if plan.get("aspectRatio") != "9:16": errors.append("aspectRatio must be 9:16")

    width, height = plan.get("width"), plan.get("height")
    valid_dimensions = not isinstance(width, bool) and not isinstance(height, bool) and (width, height) in {(720, 1280), (1080, 1920)}
    if not valid_dimensions:
        errors.append("dimensions must be 720x1280 or 1080x1920")
    if isinstance(plan.get("fps"), bool) or plan.get("fps") != 30: errors.append("fps must be 30")
    preview = plan.get("previewSeconds")
    if not _finite_number(preview) or not 6 <= preview <= 10: errors.append("previewSeconds must be a finite number between 6 and 10")
    final_hold = plan.get("finalHoldFrames")
    if not isinstance(final_hold, int) or isinstance(final_hold, bool):
        errors.append("finalHoldFrames must be an integer")
    elif min_final_hold_frames is not None and final_hold < min_final_hold_frames:
        errors.append(f"finalHoldFrames must be an integer of at least {min_final_hold_frames}")
    margin = plan.get("safeMarginPercent")
    if not _finite_number(margin) or not 8 <= margin <= 15: errors.append("safeMarginPercent must be a finite number between 8 and 15")
    if plan.get("styleRecipe") not in STYLE_RECIPES: errors.append(f"styleRecipe must be one of {sorted(STYLE_RECIPES)}")
    if plan.get("textMode") != "code-native": errors.append("textMode must be code-native")
    brush_mode = plan.get("brushMode")
    if brush_mode not in BRUSH_MODES: errors.append(f"brushMode must be one of {sorted(BRUSH_MODES)}")
    real_hand = plan.get("realHandProfile")
    if brush_mode == "real-hand-nine-action":
        if not isinstance(real_hand, dict):
            errors.append("real-hand-nine-action requires realHandProfile")
        else:
            unknown_hand = sorted(real_hand.keys() - REAL_HAND_FIELDS)
            missing_hand = sorted(REAL_HAND_FIELDS - real_hand.keys())
            if unknown_hand: errors.append(f"realHandProfile has unknown fields: {', '.join(unknown_hand)}")
            if missing_hand: errors.append(f"realHandProfile is missing fields: {', '.join(missing_hand)}")
            if real_hand.get("profile") != "gray-linen-xuan": errors.append("realHandProfile.profile must be gray-linen-xuan")
            if real_hand.get("brushAngleRange") != [80, 85]: errors.append("realHandProfile.brushAngleRange must be [80, 85]")
            if real_hand.get("armEntry") not in {"right", "lower-right"}: errors.append("realHandProfile.armEntry must be right or lower-right")
            if real_hand.get("cropBoundary") != "fabric-only": errors.append("realHandProfile.cropBoundary must be fabric-only")
            if real_hand.get("sleeveStyle") not in {"gray-linen", "project-defined"}: errors.append("realHandProfile.sleeveStyle is invalid")
            if real_hand.get("actions") != NINE_ACTIONS: errors.append("realHandProfile.actions must contain the nine ordered calligraphy actions")
            ink = real_hand.get("inkPhysics")
            if not isinstance(ink, dict):
                errors.append("realHandProfile.inkPhysics must be an object")
            else:
                unknown_ink = sorted(ink.keys() - INK_PHYSICS_FIELDS)
                missing_ink = sorted(INK_PHYSICS_FIELDS - ink.keys())
                if unknown_ink: errors.append(f"realHandProfile.inkPhysics has unknown fields: {', '.join(unknown_ink)}")
                if missing_ink: errors.append(f"realHandProfile.inkPhysics is missing fields: {', '.join(missing_ink)}")
                if ink.get("paper") != "xuan": errors.append("inkPhysics.paper must be xuan")
                ranges = {
                    "freshCoreOpacity": (0.7, 0.85), "wetEdgeOpacity": (0.15, 0.25),
                    "dryTrailOpacity": (0.35, 0.5), "dryBrushGapPercent": (15, 35),
                }
                for field, (minimum, maximum) in ranges.items():
                    value = ink.get(field)
                    if not _finite_number(value) or not minimum <= value <= maximum:
                        errors.append(f"inkPhysics.{field} must be between {minimum:g} and {maximum:g}")
                for field, minimum, maximum in [("dryingDelayFrames", 12, 24), ("diffusionDelayFrames", 2, 6)]:
                    value = ink.get(field)
                    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
                        errors.append(f"inkPhysics.{field} must be an integer between {minimum} and {maximum}")
    elif real_hand is not None:
        errors.append("realHandProfile is only allowed for real-hand-nine-action")
    if status == "PLAN_ONLY" and ({"staticArtifact", "staticArtifactSha256"} & plan.keys()): errors.append("PLAN_ONLY must not claim a static artifact or hash")

    beats = plan.get("beats")
    if not isinstance(beats, list) or not 3 <= len(beats) <= 6:
        errors.append("beats must contain 3 to 6 items")
        beats = []
    seen_ids: set[str] = set()
    previous_end = 0.0
    for index, beat in enumerate(beats):
        prefix = f"beats[{index}]"
        if not isinstance(beat, dict):
            errors.append(f"{prefix} must be an object")
            continue
        unknown_beat = sorted(beat.keys() - BEAT_FIELDS)
        if unknown_beat: errors.append(f"{prefix} has unknown fields: {', '.join(unknown_beat)}")
        beat_id = beat.get("id")
        if not isinstance(beat_id, str) or not re.match(r"^[a-z][a-z0-9-]*$", beat_id): errors.append(f"{prefix}.id must be kebab-case")
        elif beat_id in seen_ids: errors.append(f"{prefix}.id must be unique")
        else: seen_ids.add(beat_id)
        if not isinstance(beat.get("label"), str) or not beat.get("label", "").strip(): errors.append(f"{prefix}.label must be non-empty")
        if not isinstance(beat.get("copy"), str) or not beat.get("copy", "").strip(): errors.append(f"{prefix}.copy must be non-empty")
        start, end = beat.get("startSecond"), beat.get("endSecond")
        if not _finite_number(start) or not _finite_number(end) or start < 0 or end <= start:
            errors.append(f"{prefix} requires 0 <= finite startSecond < finite endSecond")
            continue
        if start < previous_end: errors.append(f"{prefix} overlaps the previous beat")
        if _finite_number(preview) and end > preview: errors.append(f"{prefix}.endSecond exceeds previewSeconds")
        previous_end = end

    if status in STATIC_STATES and base_dir is None:
        errors.append("artifact-bearing states require a base_dir; evidence cannot be verified from JSON alone")

    static_path: Path | None = None
    verified_static_hash: str | None = None
    if status in STATIC_STATES and base_dir is not None:
        static_path = _artifact(base_dir, plan.get("staticArtifact"), "staticArtifact", errors)
        if static_path is not None:
            if static_path.suffix.lower() != ".svg":
                errors.append("staticArtifact must be an SVG")
            else:
                try:
                    viewbox, flat_text = svg_viewbox_and_flat_text(static_path)
                    if valid_dimensions and viewbox != (0.0, 0.0, float(width), float(height)):
                        errors.append(f"staticArtifact viewBox must be 0 0 {width} {height}")
                    visible = {text: size for text, size, _x, _y, _estimated_width in flat_text}
                    required_text = [plan.get("title", "")] + [beat.get("label", "") for beat in beats] + [beat.get("copy", "") for beat in beats]
                    required_text += [beat["zhLabel"] for beat in beats if isinstance(beat.get("zhLabel"), str)]
                    for text in required_text:
                        if text not in visible: errors.append(f"staticArtifact is missing exact flat text: {text!r}")
                        elif visible[text] < 18: errors.append(f"staticArtifact text is too small for mobile review: {text!r}")
                    if valid_dimensions and _finite_number(margin):
                        safe_x = float(width) * float(margin) / 100
                        safe_y = float(height) * float(margin) / 100
                        for text, size, x, y, estimated_width in flat_text:
                            if x < safe_x or x + estimated_width > float(width) - safe_x or y - size < safe_y or y + size * 0.25 > float(height) - safe_y:
                                errors.append(f"staticArtifact text exceeds the {margin:g}% safe margin: {text!r}")
                except ValueError as exc:
                    errors.append(str(exc))
            claimed_static_hash = plan.get("staticArtifactSha256")
            if not isinstance(claimed_static_hash, str) or not HEX64.match(claimed_static_hash):
                errors.append("staticArtifactSha256 must be 64 lowercase hex characters")
            else:
                try:
                    verified_static_hash = sha256_static_artifact(static_path)
                    if claimed_static_hash != verified_static_hash:
                        errors.append("staticArtifactSha256 does not match the static artifact bundle")
                except ValueError as exc:
                    errors.append(str(exc))

    motion = plan.get("motionEvidence")
    if status == "MOTION_PROOF_READY":
        if not isinstance(motion, dict):
            errors.append("MOTION_PROOF_READY requires motionEvidence")
        elif base_dir is not None and static_path is not None:
            unknown_motion = sorted(motion.keys() - MOTION_FIELDS)
            if unknown_motion: errors.append(f"motionEvidence has unknown fields: {', '.join(unknown_motion)}")
            if motion.get("rendererLane") not in RENDERER_LANES: errors.append(f"rendererLane must be one of {sorted(RENDERER_LANES)}")
            owner, reviewer = motion.get("rendererOwner"), motion.get("reviewer")
            if not isinstance(owner, str) or not owner.strip(): errors.append("rendererOwner must be non-empty")
            if not isinstance(reviewer, str) or not reviewer.strip(): errors.append("reviewer must be non-empty")
            if isinstance(owner, str) and isinstance(reviewer, str) and owner.strip() and reviewer.strip() and owner.strip().casefold() == reviewer.strip().casefold(): errors.append("reviewer must be independent from rendererOwner")
            approval_hash = motion.get("staticApprovalSha256")
            if not isinstance(approval_hash, str) or not HEX64.match(approval_hash): errors.append("staticApprovalSha256 must be 64 lowercase hex characters")
            elif verified_static_hash is None or approval_hash != verified_static_hash: errors.append("staticApprovalSha256 does not match the static artifact bundle")

            frames = motion.get("frames")
            if not isinstance(frames, list) or len(frames) != 3:
                errors.append("motionEvidence.frames must contain exactly three items")
            else:
                roles, indices, paths, hashes = [], [], [], []
                for index, frame in enumerate(frames):
                    prefix = f"motionEvidence.frames[{index}]"
                    if not isinstance(frame, dict):
                        errors.append(f"{prefix} must be an object")
                        continue
                    unknown_frame = sorted(frame.keys() - FRAME_FIELDS)
                    if unknown_frame: errors.append(f"{prefix} has unknown fields: {', '.join(unknown_frame)}")
                    roles.append(frame.get("role")); indices.append(frame.get("frame")); paths.append(frame.get("path")); hashes.append(frame.get("sha256"))
                    frame_path = _artifact(base_dir, frame.get("path"), f"{prefix}.path", errors)
                    if frame_path is not None:
                        try:
                            if valid_dimensions and png_dimensions(frame_path) != (width, height): errors.append(f"{prefix} PNG dimensions must be {width}x{height}")
                            elif not valid_dimensions: png_dimensions(frame_path)
                            if frame.get("sha256") != sha256_file(frame_path): errors.append(f"{prefix}.sha256 does not match the file")
                        except ValueError as exc: errors.append(str(exc))
                if roles != ["start", "middle", "end"]: errors.append("frame roles must be ordered start, middle, end")
                if not all(isinstance(value, int) and not isinstance(value, bool) for value in indices) or indices != sorted(indices) or len(set(indices)) != 3: errors.append("frame indices must be three unique increasing integers")
                elif _finite_number(preview) and isinstance(plan.get("fps"), int) and isinstance(plan.get("finalHoldFrames"), int):
                    animation_end_frame = round(float(preview) * plan["fps"])
                    final_frame = animation_end_frame + plan["finalHoldFrames"] - 1
                    if indices[-1] < animation_end_frame:
                        errors.append("end evidence frame must be at or after the animation end frame")
                    if any(frame < 0 or frame > final_frame for frame in indices):
                        errors.append(f"evidence frame indices must be between 0 and {final_frame}")
                if not all(isinstance(value, str) for value in paths) or len(set(paths)) != 3: errors.append("frame paths must be three unique strings")
                if not all(isinstance(value, str) for value in hashes) or len(set(hashes)) != 3: errors.append("frame hashes must be three unique strings")

            proof_path_raw = motion.get("nineActionProof")
            proof_hash = motion.get("nineActionProofSha256")
            if brush_mode == "real-hand-nine-action":
                proof_path = _artifact(base_dir, proof_path_raw, "motionEvidence.nineActionProof", errors)
                if proof_path is not None:
                    try:
                        if png_dimensions(proof_path) != (1080, 1920): errors.append("motionEvidence.nineActionProof must be 1080x1920")
                        if proof_hash != sha256_file(proof_path): errors.append("motionEvidence.nineActionProofSha256 does not match the file")
                    except ValueError as exc: errors.append(str(exc))
                if not isinstance(proof_hash, str) or not HEX64.match(proof_hash): errors.append("motionEvidence.nineActionProofSha256 must be 64 lowercase hex characters")
            elif proof_path_raw is not None or proof_hash is not None:
                errors.append("nine-action proof is only allowed for real-hand-nine-action")
    elif motion is not None:
        errors.append("motionEvidence is only allowed for MOTION_PROOF_READY")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--base-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"), parse_constant=_reject_json_constant)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: cannot read plan: {exc}")
        return 1
    errors = validate(plan, args.base_dir.resolve())
    if errors:
        print("FAIL: storyboard evidence is not ready")
        for error in errors: print(f"- {error}")
        return 1
    print(f"PASS: {args.plan} is {plan['status']} with verified supplied evidence")
    return 0


if __name__ == "__main__":
    sys.exit(main())

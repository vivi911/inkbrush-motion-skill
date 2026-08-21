(() => {
  "use strict";

  const stage = document.querySelector("#ink-stage");
  const path = document.querySelector("#river-path");
  const diffusion = document.querySelector("#river-diffusion");
  const dryPath = document.querySelector("#river-dry");
  const dryMask = document.querySelector("#river-dry-mask");
  const brush = document.querySelector("#brush");
  const movingBrush = document.querySelector("#moving-brush");
  const wetEdge = document.querySelector(".wet-edge");
  const replayButton = document.querySelector("#replay");
  const status = document.querySelector("#motion-status");
  const journeyFrame = document.querySelector(".journey-frame");
  const waypoints = [...document.querySelectorAll(".waypoint")];
  const captions = [...document.querySelectorAll(".lesson-caption")];
  const result = document.querySelector(".journey-result");
  const reveals = [...waypoints, ...captions, result].filter(Boolean);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const previewMode = new URLSearchParams(window.location.search).get("preview");
  const timing = window.INKBRUSH_TIMING;

  if (!stage || !path || !diffusion || !dryPath || !dryMask || !brush || !movingBrush || !wetEdge || !replayButton || !status || !journeyFrame || !timing) return;

  const duration = timing.durationMs;
  const totalFrames = duration / 1000 * timing.fps;
  const diffusionDelay = timing.inkDelays.diffusionFrames / totalFrames;
  const dryingDelay = timing.inkDelays.dryingFrames / totalFrames;
  const pathLength = path.getTotalLength();
  let frameId = 0;
  let loopTimer = 0;
  let activePose = -1;

  const brushPoses = [
    { src: "assets/brush-poses-v3/pose-01.png", anchor: [315, 620] },
    { src: "assets/brush-poses-v3/pose-02.png", anchor: [315, 620] },
    { src: "assets/brush-poses-v3/pose-03.png", anchor: [315, 620] },
    { src: "assets/brush-poses-v3/pose-04.png", anchor: [315, 620] },
    { src: "assets/brush-poses-v3/pose-05.png", anchor: [315, 620] },
    { src: "assets/brush-poses-v3/pose-06.png", anchor: [315, 620] },
    { src: "assets/brush-poses-v3/pose-07.png", anchor: [315, 620] },
    { src: "assets/brush-poses-v3/pose-08.png", anchor: [315, 620] },
    // LEAVE uses its own clean lifted pose and keeps the bristles
    // 40 px above the completed stroke so the final hold reads as off-paper.
    { src: "assets/brush-poses-v3/pose-09.png", anchor: [315, 662] },
  ];
  brushPoses.forEach(({ src }) => { const image = new Image(); image.src = src; });

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const ease = (value) => value * value * (3 - 2 * value);

  function poseIndexFor(progress) {
    const index = timing.breaks.findIndex((threshold) => progress < threshold);
    return index === -1 ? brushPoses.length - 1 : index;
  }

  function strokeProgress(progress) {
    if (progress < timing.strokeSegments[0][0]) return 0;
    for (const [start, end, from, to] of timing.strokeSegments) {
      if (progress < end) return from + (to - from) * ease(clamp((progress - start) / (end - start), 0, 1));
    }
    return 1;
  }

  function placeBrush(progress, poseIndex) {
    const distance = clamp(progress, 0, 1) * pathLength;
    const point = path.getPointAtLength(distance);
    const pose = brushPoses[poseIndex];
    if (poseIndex !== activePose) {
      movingBrush.setAttribute("href", pose.src);
      movingBrush.setAttribute("x", String(-pose.anchor[0]));
      movingBrush.setAttribute("y", String(-pose.anchor[1]));
      activePose = poseIndex;
    }
    brush.setAttribute("transform", `translate(${point.x.toFixed(2)} ${point.y.toFixed(2)})`);
    wetEdge.style.opacity = poseIndex === brushPoses.length - 1 ? "0" : "";
    stage.dataset.brushProgress = clamp(progress, 0, 1).toFixed(4);
    stage.dataset.brushPose = String(poseIndex + 1).padStart(2, "0");
  }

  function paint(progress) {
    const stroke = strokeProgress(progress);
    const bloomProgress = clamp((stroke - diffusionDelay) / (1 - diffusionDelay), 0, 1);
    const dryProgress = clamp((stroke - dryingDelay) / (1 - dryingDelay), 0, 1);
    const poseIndex = poseIndexFor(progress);
    const distance = stroke * pathLength;
    const activeSpan = pathLength * 0.075;
    const activeLength = Math.max(0.01, Math.min(distance, activeSpan));
    const activeStart = Math.max(0, distance - activeSpan);

    path.style.strokeDasharray = `${activeLength} ${pathLength + activeSpan}`;
    path.style.strokeDashoffset = String(-activeStart);
    path.style.opacity = String(0.78 * (1 - clamp((progress - timing.breaks.at(-1)) / (1 - timing.breaks.at(-1)), 0, 1)));
    diffusion.style.strokeDashoffset = String(pathLength * (1 - ease(bloomProgress)));
    dryMask.style.strokeDashoffset = String(pathLength * (1 - ease(dryProgress)));
    placeBrush(stroke, poseIndex);

    reveals.forEach((reveal) => {
      const threshold = timing.knowledgeThresholds[reveal.dataset.thresholdKey] ?? 0;
      const endThreshold = timing.knowledgeThresholds[reveal.dataset.endThresholdKey] ?? 1.01;
      reveal.classList.toggle("is-visible", stroke >= threshold && stroke < endThreshold);
    });

    if (progress >= 1) {
      status.textContent = "Evidence verified";
      brush.style.opacity = "1";
      stage.dataset.motionState = "complete";
      journeyFrame.dataset.motionState = "complete";
    } else {
      status.textContent = progress < timing.breaks[0]
        ? "Poising the brush…"
        : progress < timing.breaks[2]
          ? "Setting the ink…"
          : progress < timing.breaks[3]
            ? "Painting context and action…"
            : "Checking evidence…";
      brush.style.opacity = "1";
      stage.dataset.motionState = "painting";
      journeyFrame.dataset.motionState = "painting";
    }
  }

  function reset() {
    cancelAnimationFrame(frameId);
    clearTimeout(loopTimer);
    journeyFrame.classList.add("is-resetting");
    [diffusion, dryMask].forEach((line) => {
      line.style.strokeDasharray = `${pathLength} ${pathLength}`;
      line.style.strokeDashoffset = String(pathLength);
    });
    path.style.strokeDasharray = `0.01 ${pathLength}`;
    path.style.strokeDashoffset = "0";
    path.style.opacity = "0.78";
    reveals.forEach((reveal) => reveal.classList.remove("is-visible"));
    journeyFrame.dataset.motionState = "reset";
    journeyFrame.getBoundingClientRect();
    journeyFrame.classList.remove("is-resetting");
    brush.style.opacity = "1";
    paint(0);
  }

  function play() {
    reset();
    if (reduceMotion.matches || previewMode === "static") {
      paint(1);
      stage.dataset.motionState = "static";
      journeyFrame.dataset.motionState = "static";
      return;
    }

    const startedAt = performance.now();
    const tick = (now) => {
      const progress = clamp((now - startedAt) / duration, 0, 1);
      paint(progress);
      if (progress < 1) {
        frameId = requestAnimationFrame(tick);
      } else if (previewMode !== "once") {
        loopTimer = window.setTimeout(play, 3200);
      }
    };
    frameId = requestAnimationFrame(tick);
  }

  replayButton.addEventListener("click", play);
  reduceMotion.addEventListener?.("change", play);
  play();
})();

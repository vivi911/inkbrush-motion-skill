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

  if (!stage || !path || !diffusion || !dryPath || !dryMask || !brush || !movingBrush || !wetEdge || !replayButton || !status || !journeyFrame) return;

  const duration = 9200;
  const totalFrames = duration / 1000 * 30;
  const diffusionDelay = 5 / totalFrames;
  const dryingDelay = 12 / totalFrames;
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
    const breaks = [0.08, 0.14, 0.22, 0.58, 0.68, 0.78, 0.88, 0.96];
    const index = breaks.findIndex((threshold) => progress < threshold);
    return index === -1 ? brushPoses.length - 1 : index;
  }

  function strokeProgress(progress) {
    const segment = (start, end, from, to) => from + (to - from) * ease(clamp((progress - start) / (end - start), 0, 1));
    if (progress < 0.08) return 0;
    if (progress < 0.14) return segment(0.08, 0.14, 0, 0.01);
    if (progress < 0.22) return segment(0.14, 0.22, 0.01, 0.04);
    if (progress < 0.58) return segment(0.22, 0.58, 0.04, 0.60);
    if (progress < 0.68) return segment(0.58, 0.68, 0.60, 0.72);
    if (progress < 0.78) return segment(0.68, 0.78, 0.72, 0.86);
    if (progress < 0.88) return segment(0.78, 0.88, 0.86, 0.94);
    if (progress < 0.96) return segment(0.88, 0.96, 0.94, 1);
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
    path.style.opacity = String(0.78 * (1 - clamp((progress - 0.96) / 0.04, 0, 1)));
    diffusion.style.strokeDashoffset = String(pathLength * (1 - ease(bloomProgress)));
    dryMask.style.strokeDashoffset = String(pathLength * (1 - ease(dryProgress)));
    placeBrush(stroke, poseIndex);

    reveals.forEach((reveal) => {
      const threshold = Number(reveal.dataset.threshold || 0);
      const endThreshold = Number(reveal.dataset.endThreshold || 1.01);
      reveal.classList.toggle("is-visible", stroke >= threshold && stroke < endThreshold);
    });

    if (progress >= 1) {
      status.textContent = "Evidence verified";
      brush.style.opacity = "1";
      stage.dataset.motionState = "complete";
      journeyFrame.dataset.motionState = "complete";
    } else {
      status.textContent = progress < 0.08
        ? "Poising the brush…"
        : progress < 0.22
          ? "Setting the ink…"
          : progress < 0.58
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

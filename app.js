(() => {
  "use strict";

  const stage = document.querySelector("#ink-stage");
  const path = document.querySelector("#river-path");
  const diffusion = document.querySelector("#river-diffusion");
  const brush = document.querySelector("#brush");
  const replayButton = document.querySelector("#replay");
  const status = document.querySelector("#motion-status");
  const journeyFrame = document.querySelector(".journey-frame");
  const waypoints = [...document.querySelectorAll(".waypoint")];
  const captions = [...document.querySelectorAll(".lesson-caption")];
  const result = document.querySelector(".journey-result");
  const reveals = [...waypoints, ...captions, result].filter(Boolean);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const previewMode = new URLSearchParams(window.location.search).get("preview");

  if (!stage || !path || !diffusion || !brush || !replayButton || !status || !journeyFrame) return;

  const duration = 9200;
  const diffusionDelay = 0.02;
  const pathLength = path.getTotalLength();
  let frameId = 0;
  let loopTimer = 0;

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const ease = (value) => value * value * (3 - 2 * value);

  function placeBrush(progress) {
    const distance = clamp(progress, 0, 1) * pathLength;
    const point = path.getPointAtLength(distance);
    const previous = path.getPointAtLength(Math.max(0, distance - 2));
    const direction = Math.atan2(point.y - previous.y, point.x - previous.x) * 180 / Math.PI;
    brush.setAttribute("transform", `translate(${point.x.toFixed(2)} ${point.y.toFixed(2)}) rotate(${(direction - 90).toFixed(2)})`);
  }

  function paint(progress) {
    const eased = ease(progress);
    const bloomProgress = clamp((progress - diffusionDelay) / (1 - diffusionDelay), 0, 1);

    path.style.strokeDashoffset = String(pathLength * (1 - eased));
    diffusion.style.strokeDashoffset = String(pathLength * (1 - ease(bloomProgress)));
    placeBrush(eased);

    reveals.forEach((reveal) => {
      const threshold = Number(reveal.dataset.threshold || 0);
      const endThreshold = Number(reveal.dataset.endThreshold || 1.01);
      reveal.classList.toggle("is-visible", eased >= threshold && eased < endThreshold);
    });

    if (progress >= 1) {
      status.textContent = "Evidence verified";
      brush.style.opacity = "0";
      stage.dataset.motionState = "complete";
      journeyFrame.dataset.motionState = "complete";
    } else {
      status.textContent = progress < 0.32
        ? "Painting context…"
        : progress < 0.62
          ? "Choosing one action…"
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
    [path, diffusion].forEach((line) => {
      line.style.strokeDasharray = `${pathLength} ${pathLength}`;
      line.style.strokeDashoffset = String(pathLength);
    });
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

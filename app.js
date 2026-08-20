(() => {
  "use strict";

  const stage = document.querySelector("#ink-stage");
  const path = document.querySelector("#river-path");
  const diffusion = document.querySelector("#river-diffusion");
  const brush = document.querySelector("#brush");
  const replayButton = document.querySelector("#replay");
  const status = document.querySelector("#motion-status");
  const waypoints = [...document.querySelectorAll(".waypoint")];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const previewMode = new URLSearchParams(window.location.search).get("preview");

  if (!stage || !path || !diffusion || !brush || !replayButton || !status) return;

  const duration = 8200;
  const diffusionDelay = 0.018;
  const pathLength = path.getTotalLength();
  let frameId = 0;

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const ease = (value) => value * value * (3 - 2 * value);

  function placeBrush(progress) {
    const distance = clamp(progress, 0, 1) * pathLength;
    const point = path.getPointAtLength(distance);
    const before = path.getPointAtLength(Math.max(0, distance - 2));
    const after = path.getPointAtLength(Math.min(pathLength, distance + 2));
    const angle = Math.atan2(after.y - before.y, after.x - before.x) * 180 / Math.PI + 90;
    brush.setAttribute("transform", `translate(${point.x.toFixed(2)} ${point.y.toFixed(2)}) rotate(${angle.toFixed(2)})`);
  }

  function paint(progress) {
    const eased = ease(progress);
    const bloomProgress = clamp((progress - diffusionDelay) / (1 - diffusionDelay), 0, 1);

    path.style.strokeDashoffset = String(pathLength * (1 - eased));
    diffusion.style.strokeDashoffset = String(pathLength * (1 - ease(bloomProgress)));
    placeBrush(eased);

    waypoints.forEach((waypoint) => {
      const threshold = Number(waypoint.dataset.threshold || 0);
      waypoint.classList.toggle("is-visible", eased >= threshold);
    });

    if (progress >= 1) {
      status.textContent = "Complete";
      brush.style.opacity = "0";
      stage.dataset.motionState = "complete";
    } else {
      status.textContent = progress < 0.08 ? "Loading ink…" : "Painting…";
      brush.style.opacity = "1";
      stage.dataset.motionState = "painting";
    }
  }

  function reset() {
    cancelAnimationFrame(frameId);
    stage.classList.add("is-resetting");
    [path, diffusion].forEach((line) => {
      line.style.strokeDasharray = `${pathLength} ${pathLength}`;
      line.style.strokeDashoffset = String(pathLength);
    });
    waypoints.forEach((waypoint) => waypoint.classList.remove("is-visible"));
    stage.getBoundingClientRect();
    stage.classList.remove("is-resetting");
    brush.style.opacity = "1";
    paint(0);
  }

  function play() {
    reset();
    if (reduceMotion.matches || previewMode === "static") {
      paint(1);
      return;
    }

    const startedAt = performance.now();
    const tick = (now) => {
      const progress = clamp((now - startedAt) / duration, 0, 1);
      paint(progress);
      if (progress < 1) frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
  }

  replayButton.addEventListener("click", play);
  reduceMotion.addEventListener?.("change", play);
  play();
})();

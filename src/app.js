import { exits } from "./data/exits.js";
import renderExitCard from "./components/exit-card.js";
import { shareToX, nativeShare } from "./utils/share.js";

// ── App init ──
function init() {
  renderFeed();
}

// ── Feed ──
function renderFeed() {
  const feed = document.getElementById("feed");
  if (!feed) return;

  feed.innerHTML = "";

  exits.forEach((exit) => {
    const card = renderExitCard(exit, {
      onCounterClick: handleCounterClick,
      onShare: handleShare,
    });
    feed.appendChild(card);
  });
}

// ── Handlers ──
function handleCounterClick(exit) {
  // TODO Phase 2: open modal with list of people who exited this
  console.log(`${exit.exitCount} people exited ${exit.what}`);
  alert(`${exit.exitCount.toLocaleString()} people exited "${exit.what}"`);
}

async function handleShare(exit) {
  const shared = await nativeShare(exit);
  if (!shared) {
    // Fallback to X
    shareToX(exit);
  }
}

// ── Boot ──
document.addEventListener("DOMContentLoaded", init);

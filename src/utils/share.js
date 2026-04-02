// Share utilities — swap for Android native share sheet in Phase 3

// Generate shareable text for an exit post
export function getShareText(exit) {
  const alt = exit.alternative
    ? `→ ${exit.alternative}`
    : "→ nothing, and that's the point";
  return `I exited ${exit.what}. ${alt}\n\n#exittech #exitculture\nexit.tech`;
}

// Share to X/Twitter
export function shareToX(exit) {
  const text = encodeURIComponent(getShareText(exit));
  window.open(`https://x.com/intent/tweet?text=${text}`, "_blank");
}

// Share to Farcaster
export function shareToFarcaster(exit) {
  const text = encodeURIComponent(getShareText(exit));
  window.open(`https://warpcast.com/~/compose?text=${text}`, "_blank");
}

// Native Web Share API (mobile)
export async function nativeShare(exit) {
  if (!navigator.share) return false;
  try {
    await navigator.share({
      title: `I exited ${exit.what}`,
      text: getShareText(exit),
      url: "https://exit.tech",
    });
    return true;
  } catch {
    return false;
  }
}

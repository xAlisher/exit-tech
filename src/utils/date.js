// Date utilities — pure functions, no side effects

// "2023-06" → "Jun 2023"
export function formatExitDate(yearMonth) {
  if (!yearMonth) return "";
  const [year, month] = yearMonth.split("-");
  const date = new Date(year, parseInt(month) - 1);
  return date.toLocaleDateString("en-US", { month: "short", year: "numeric" });
}

// "2023-06" → "1 year ago" / "3 months ago"
export function timeAgo(yearMonth) {
  if (!yearMonth) return "";
  const [year, month] = yearMonth.split("-");
  const then = new Date(year, parseInt(month) - 1);
  const now = new Date();
  const months = (now.getFullYear() - then.getFullYear()) * 12 +
    (now.getMonth() - then.getMonth());
  if (months < 1) return "this month";
  if (months < 12) return `${months}mo ago`;
  const years = Math.floor(months / 12);
  return years === 1 ? "1 year ago" : `${years} years ago`;
}

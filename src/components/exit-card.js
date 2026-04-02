import { formatExitDate } from "../utils/date.js";

// Renders a single exit post card
// Input: exit object (shape from src/data/exits.js)
// Output: <article class="exit-card"> DOM element

export default function renderExitCard(exit, { onCounterClick, onShare } = {}) {
  const article = document.createElement("article");
  article.className = "exit-card";

  // Header — author + date
  const header = document.createElement("div");
  header.className = "exit-card__header";

  const author = document.createElement("span");
  author.className = "exit-card__author mono";
  author.textContent = `@${exit.authorHandle}`;

  const date = document.createElement("span");
  date.className = "exit-card__date";
  date.textContent = formatExitDate(exit.date);

  header.appendChild(author);
  header.appendChild(date);

  // What — the exited thing, strikethrough
  const what = document.createElement("div");
  what.className = "exit-card__what";
  what.textContent = exit.what;

  // Almost out badge
  if (exit.almostOut) {
    const almostBadge = document.createElement("span");
    almostBadge.className = "almost-out-badge";
    almostBadge.textContent = "almost out";
    what.appendChild(document.createTextNode(" "));
    what.appendChild(almostBadge);
  }

  // Why — the reason
  const why = document.createElement("p");
  why.className = "exit-card__why";
  why.textContent = exit.why;

  // Alternative
  const altRow = document.createElement("div");
  altRow.className = "exit-card__alternative";

  const arrow = document.createElement("span");
  arrow.className = "exit-card__alternative-arrow";
  arrow.textContent = "→";

  let altContent;
  if (exit.alternative) {
    if (exit.alternativeUrl) {
      altContent = document.createElement("a");
      altContent.href = exit.alternativeUrl;
      altContent.target = "_blank";
      altContent.rel = "noopener noreferrer";
      altContent.textContent = exit.alternative;
    } else {
      altContent = document.createElement("span");
      altContent.textContent = exit.alternative;
    }
  } else {
    altContent = document.createElement("span");
    altContent.style.fontStyle = "italic";
    altContent.textContent = "nothing, and that's the point";
  }

  altRow.appendChild(arrow);
  altRow.appendChild(altContent);

  // Footer — category tag + counter + share
  const footer = document.createElement("div");
  footer.className = "exit-card__footer";

  // Category tag
  const tag = document.createElement("span");
  tag.className = `tag tag--${exit.category}`;
  tag.textContent = exit.category;

  // Counter badge
  const counter = document.createElement("button");
  counter.className = "counter-badge";
  counter.setAttribute("aria-label", `${exit.exitCount} people exited this`);
  counter.innerHTML = `
    <span class="counter-badge__number">${exit.exitCount.toLocaleString()}</span>
    <span>also exited</span>
  `;
  if (onCounterClick) {
    counter.addEventListener("click", (e) => {
      e.stopPropagation();
      onCounterClick(exit);
    });
  }

  // Share button
  const shareBtn = document.createElement("button");
  shareBtn.className = "share-btn";
  shareBtn.setAttribute("aria-label", "Share this exit");
  shareBtn.textContent = "↗ share";
  if (onShare) {
    shareBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      onShare(exit);
    });
  }

  footer.appendChild(tag);
  footer.appendChild(counter);
  footer.appendChild(shareBtn);

  // Assemble
  article.appendChild(header);
  article.appendChild(what);
  article.appendChild(why);
  article.appendChild(altRow);
  article.appendChild(footer);

  return article;
}

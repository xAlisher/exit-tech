# Local drafting voice — distilled from review edits

Fed verbatim into every `draft_local.py` prompt. Grows by one review at a time:
after Claude reviews a draft, diff `.review/<slug>.draft.yaml` against the
merged file and distill what changed into rules here. Keep it under ~30 rules;
merge near-duplicates; every rule cites the review that taught it.

## Facts

1. Never assert how a company uses data or makes money ("sells your viewing
   history") unless the research pack confirms it. The safe form describes what
   the product *does to the user*: "optimizes for retention, not satisfaction".
   This is the model's single most reliable failure — **expect a data-use
   overclaim in the tagline AND the first why-bullet of nearly every draft**, and
   rewrite both as a matter of course. Worse, the claim is sometimes verifiably
   false, not just unbacked (gmail draft: "Google scans email for AI training" —
   Gmail stopped ad-scanning in 2017). (netflix: "sold to studios" cut.
   google-docs: "Your draft is their training data" + "documents train the
   models" cut. gmail: "correspondence is training data" cut. google-search:
   "Your questions are the product" + "every query builds a profile sold to
   advertisers" cut.)
2. In extract steps, concrete beats vague: name the exact URL or menu path
   (netflix.com/account/getmyinfo), not "request your data archive". Watch for
   the opposite failure too — the model invents plausible-but-wrong menu paths;
   verify them and replace with the real URL. (netflix review: vague step
   rewritten to a URL. google-docs review: invented "One Google > Data &
   personalization" replaced with takeout.google.com.)

## Taste

3. Taglines: emotional precision beats snark or cliché. "They know what makes
   you cry" survived review; "subscription trap" was cut as stock phrase, and
   "you are the product" was cut as the most stock phrase in the genre —
   replaced with a lived moment: "Three hours gone, and you can't name one
   video." Describe the user's experience, not the industry critique. A tagline
   can name the dependency's *structure* as lived cost rather than emotion —
   "You don't have a file. You have a link." — and still beat the punchy
   overclaim it replaced.
   (netflix, tiktok, google-docs reviews)
4. The habit angle is your best contribution: behavioral insight ("break the
   habit of mindless scrolling through menus") outranks feature comparisons of
   alternatives. Always ask: what does the user *do* with this dependency daily?
   (netflix review: that line was kept verbatim)
5. Two why-bullets are enough, and each must name a mechanism (catalog rotates,
   autoplay chains episodes) — not a vibe ("it's bad for you").

## Structure

6. The first prompt line should make the user's agent interview before
   recommending ("ask me what I actually watched last month"). The model often
   leads with a "help me decide between X, Y, Z" line and buries the interview
   second — reorder so the interview leads and the options follow from it.
   (netflix review: added. google-docs review: "decide whether to switch" and
   the interview line were swapped.)
7. Method lines ("ask me about my hardware") belong in `prompt`, not in
   alternative `note` fields. Notes state when that alternative is the right
   pick, in one line.
8. Never emit a path with an empty `alternatives` list. If a path has no
   concrete alternatives, its content belongs in `prompt`.
   (tiktok review: empty "grow" path cut)
9. A source listing an alternative makes it *claimable*, not *good advice*.
   Only list alternatives that plausibly serve the same need — and when nothing
   does, say so: "Nothing" is a valid alternative, honestly framed. Alternatives
   may cross-link to sibling exit pages (exit.tech/exit/<id>.html). A bare
   catalog listing (awesome-selfhosted is an inclusion list, not an endorsement)
   is the weakest possible backing — don't stand up a dedicated route on one
   alone; require at least one *editorial* recommender (Privacy Guides,
   switching.software, awesome-privacy) before promoting it past the prompt.
   (tiktok review: DTube cut as dead-end advice; "Nothing" added. google-docs
   review: "Docs (La Suite)" pulled — only awesome-selfhosted listed it; Privacy
   Guides recommends only CryptPad in that category.)
10. Don't oversell the switch: if the alternative will feel worse in the way
    that matters (slower, less dopamine), the note says so plainly — that
    honesty is the brand.
    (tiktok review: PeerTube note rewritten)

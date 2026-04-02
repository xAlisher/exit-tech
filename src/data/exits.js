// SOURCE OF TRUTH — all components consume this shape
// When switching to Waku/Codex, only this file changes

export const EXIT_CATEGORIES = {
  digital: "Digital",
  financial: "Financial",
  relational: "Relational",
  institutional: "Institutional",
  substance: "Substance",
};

export const PRIVACY_LEVELS = {
  public: "Public",
  community: "Community",
  private: "Private",
};

// Shape definition — every exit object looks like this
export const EXIT_SHAPE = {
  id: String,
  what: String,              // what was exited
  why: String,               // short reason
  alternative: String,       // what replaced it (or null)
  alternativeUrl: String,    // link to alternative (or null)
  category: String,          // key from EXIT_CATEGORIES
  date: String,              // "YYYY-MM" format
  exitCount: Number,         // how many others exited this
  almostOut: Boolean,        // soft pre-exit state
  privacy: String,           // key from PRIVACY_LEVELS
  authorId: String,
  authorHandle: String,
};

// Mock data — replace with Waku/Codex in Phase 4
export const exits = [
  {
    id: "001",
    what: "Google Drive",
    why: "Every file I own, indexed and profiled. Realised I was paying with data, not money.",
    alternative: "Proton Drive",
    alternativeUrl: "https://proton.me/drive",
    category: "digital",
    date: "2023-06",
    exitCount: 1243,
    almostOut: false,
    privacy: "public",
    authorId: "u1",
    authorHandle: "alisher",
  },
  {
    id: "002",
    what: "Spotify",
    why: "Algorithmic taste narrowing. My listening became a product.",
    alternative: "Navidrome + Funkwhale",
    alternativeUrl: "https://navidrome.org",
    category: "digital",
    date: "2022-11",
    exitCount: 892,
    almostOut: false,
    privacy: "public",
    authorId: "u1",
    authorHandle: "alisher",
  },
  {
    id: "003",
    what: "Instagram",
    why: "Attention extraction dressed as community.",
    alternative: null,
    alternativeUrl: null,
    category: "digital",
    date: "2024-01",
    exitCount: 3847,
    almostOut: false,
    privacy: "public",
    authorId: "u2",
    authorHandle: "senty",
  },
  {
    id: "004",
    what: "30-year mortgage",
    why: "Renting money from a bank for the right to own what I live in.",
    alternative: "Community land trust",
    alternativeUrl: null,
    category: "financial",
    date: "2024-09",
    exitCount: 47,
    almostOut: false,
    privacy: "community",
    authorId: "u3",
    authorHandle: "fergie",
  },
  {
    id: "005",
    what: "iPhone",
    why: "Walled garden with a premium lock-in tax.",
    alternative: "GrapheneOS on Pixel",
    alternativeUrl: "https://grapheneos.org",
    category: "digital",
    date: "2024-03",
    exitCount: 612,
    almostOut: true,
    privacy: "public",
    authorId: "u4",
    authorHandle: "anon",
  },
];

// Mock profiles
export const profiles = [
  {
    id: "u1",
    handle: "alisher",
    bio: "Experience designer. Building sovereignty infrastructure.",
    exitCount: 12,
    joinedDate: "2024-01",
  },
  {
    id: "u2",
    handle: "fergie",
    bio: "Exit.tech builder",
    exitCount: 23,
    joinedDate: "2024-02",
  },
];

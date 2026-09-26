-- wow-worker D1 schema. Apply with:
--   npx wrangler d1 execute wow-data --remote --file=schema.sql
-- No character name, no account, no raw IP is ever stored (see src/index.ts).

-- One row per accepted upload. delete_hash = SHA-256 of the deletion code shown to the player,
-- so they can erase their own data later (GDPR right to erasure) without any account.
CREATE TABLE IF NOT EXISTS submissions (
  id           TEXT PRIMARY KEY,
  received_at  INTEGER NOT NULL,
  addon        TEXT,
  client       TEXT,
  n_meas       INTEGER NOT NULL DEFAULT 0,
  n_prices     INTEGER NOT NULL DEFAULT 0,
  delete_hash  TEXT NOT NULL
);

-- In-game measurements (character sheet, pet, rating conversion). sig dedupes the same record
-- uploaded twice (players re-upload a file that still holds older records).
CREATE TABLE IF NOT EXISTS measurements (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  submission_id  TEXT NOT NULL,
  kind           TEXT NOT NULL,
  class          TEXT,
  level          INTEGER,
  recorded_at    INTEGER,
  data           TEXT NOT NULL,
  sig            TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_meas_kind ON measurements (kind, class, level);
CREATE INDEX IF NOT EXISTS idx_meas_sub ON measurements (submission_id);

-- Auction house scans: lowest unit buyout + quantity per item, per realm/faction/scan time.
CREATE TABLE IF NOT EXISTS ah_prices (
  realm          TEXT NOT NULL,
  faction        TEXT NOT NULL,
  item_id        INTEGER NOT NULL,
  scanned_at     INTEGER NOT NULL,
  unit_min       INTEGER NOT NULL,
  qty            INTEGER NOT NULL,
  auctions       INTEGER NOT NULL,
  submission_id  TEXT NOT NULL,
  PRIMARY KEY (realm, faction, item_id, scanned_at)
);
CREATE INDEX IF NOT EXISTS idx_ah_item ON ah_prices (item_id, scanned_at);
CREATE INDEX IF NOT EXISTS idx_ah_sub ON ah_prices (submission_id);

-- Upload rate limit per salted IP hash and hour window (rows older than a day are purged).
CREATE TABLE IF NOT EXISTS rate (
  key     TEXT NOT NULL,
  window  INTEGER NOT NULL,
  count   INTEGER NOT NULL,
  PRIMARY KEY (key, window)
);

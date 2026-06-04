-- promotions_004.sql — Structured single-source content model for the PBuilder.
--
-- The promo landing page lived in TWO places that drifted: the dashboard
-- preview (`proposal_html`) and the WP page body (pushed via REST). On the
-- AmaWaterways Egypt promo this drift meant a fabricated itinerary had to be
-- hand-fixed in both copies independently.
--
-- This migration introduces a single source of truth:
--   * content_model    — canonical structured JSON (hero, overview, day-by-day
--                        itinerary, inclusions, reserve CTA, lead form, TICO).
--                        The dashboard's TS renderer (lib/marketing/promo-render.ts)
--                        is the ONLY renderer; it turns this model into both the
--                        preview HTML and the WP page body. Edit the model →
--                        both regenerate, so they can never drift again.
--   * wp_content_html  — cache of the last-rendered WP page body that was pushed
--                        to the draft WP page. Lets promo/dispatch stay a dumb
--                        "flip to publish" step (no HTML generation).
--   * content_model_at — when the model was last edited (audit convenience).
--
-- Backfill is lazy: existing promos keep content_model NULL until first edited
-- through the structured surface (seeded from their scalar columns on open).

ALTER TABLE promotions ADD COLUMN content_model TEXT;
ALTER TABLE promotions ADD COLUMN wp_content_html TEXT;
ALTER TABLE promotions ADD COLUMN content_model_at TEXT;

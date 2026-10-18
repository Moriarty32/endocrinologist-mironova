# Decisions and open questions

## Fixed for this prototype

- **Reference-matched landing.** `landing.css` is a separate visual layer built from the supplied mockup: three-column hero, mint section bands, white bordered cards, compact Inter typography and the same section order. `styles.css` remains the base for articles and legal pages.
- **Multi-page architecture.** The home page stays conversion-focused; services, diseases, articles, about, prices, reviews, contacts, FAQ and documents are separate pages with shared header, footer, forms and visual language.
- **Single content source.** `content/site_content.py` defines services, diseases, articles, prices, contacts and navigation groups. `tools/build_site.py` generates pages, `assets/js/site-data.js`, sitemap and legacy redirects. Generated directories should not be edited by hand.
- **Shared shell.** `assets/js/site.js` renders the sticky header, desktop Mega Menu, mobile accordion drawer, footer and price values. The header is intentionally data-driven so changing a title or URL in the source updates every page.
- **Static CMS prototype.** The data structure mirrors future CMS entities, but there is no admin UI. A production CMS would expose the same fields and regenerate or server-render pages.
- **No backend yet.** Forms validate client-side and save only non-medical contact fields in `sessionStorage` for the demo. A production integration must add a server-side endpoint, anti-spam, consent logging and access control.
- **Quiz state in `sessionStorage`.** Answers persist for the current tab only. The result is an information memo, never a diagnosis or triage recommendation.
- **No medical content in analytics.** `window.dataLayer` receives event names and non-medical metadata only. Topic selection is reduced to a boolean.
- **Placeholder photography.** Portraits and article thumbnails are cropped from the supplied reference and are explicitly temporary. The hero uses a wide composite so the doctor remains visible across the full block. Replace with licensed source photography before launch.
- **Document placeholders.** Certificate cards contain no invented numbers, seals or registry data.
- **Self-hosted fonts.** Inter, Golos Text and Lora are shipped as WOFF2 with Cyrillic and Latin subsets.
- **Native dialogs.** `<dialog>` supplies focus containment and Escape handling; custom JS adds state and scroll management.

## Open questions before launch

1. Legal operator: ИП or medical organization, ОГРНИП/ИНН, address.
2. Medical license details and the legal scope of a first remote consultation.
3. Actual platform for video calls, recording policy and medical documentation.
4. CRM/endpoint for leads, retention periods, role-based access and audit logging.
5. Whether online booking slots and payment are available at launch.
6. Final prices, duration, cancellation/refund rules and follow-up policy.
7. Real photographs, video address, education/ accreditation documents and doctor bio.
8. Medical and legal review of all quiz results, FAQ answers and article copy.
9. Analytics provider and consent banner requirements.
10. Whether the site remains a demo or is replaced by a CMS-driven production build.
11. Review moderation process, verified external profiles and consent storage.
12. Clinical review of every service/disease page and the exact scope of online care.

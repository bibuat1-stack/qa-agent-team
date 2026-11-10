# Glossary

Pack-specific terms. Standard testing terms (heuristic, oracle, tour, attack, SBTM, PO, smoke, regression) keep their RST and context-driven meaning.

- Driver: whatever operates the product for one probe (a browser subagent, an automation script).
- Probe: one focused thing you try on the product.
- User action: anything a person or agent who matters can do with the product, or can reasonably believe they can do from what it shows them (pressing something styled as a button, typing in a field, using Back).
- Target setting: a condition that changes what users experience and that the charter commits to covering (screen size, browser, signed in or out, language, no JavaScript).
- Evidence folder: from setup. The session folder is one session's dated folder inside it.
- BUG-NN: a numbered bug entry. Numbering is per project and continues across sessions (a fix charter keeps the old numbers); the next is one more than the highest in the project's bug list (its latest report's bug index, unless house rules or setup say otherwise). If another session may be numbering in the same project at once, add your name so IDs can't collide (`BUG-rex-04`). Can't find the list? Use a provisional number (`skills/BUG-new-1`) and ask. Bugs in your test tools belong to the project that owns them; in mixed lists, prefix the project (`shop/BUG-03`).

# Priority

**Priority** = how soon the bug should be fixed. QA proposes it; the product owner decides.

| Priority | Meaning | Examples |
|----------|---------|----------|
| **High** | Fix in the current sprint / before release: core flow broken with no workaround, blocks testing, data loss, security, money, or affects many users | Checkout always fails; XSS executes; search returns wrong products |
| **Medium** | Fix in a normal planning cycle: important function wrong but a workaround exists | Search ignores very short terms; filter resets after page reload |
| **Low** | Fix when convenient; may be accepted as-is: cosmetic or rare edge case | Typo, misaligned icon, inconsistent capitalisation |

## How to decide

1. What can the user no longer do, and is there a workaround?
2. How many users hit it, how often, and how visible is it?
3. Is data, security, money or a release deadline involved? If yes, lean to **High**.
4. Write one line of justification, e.g. *"Medium: users cannot find products by 1–2 letter terms; workaround is typing more letters."*

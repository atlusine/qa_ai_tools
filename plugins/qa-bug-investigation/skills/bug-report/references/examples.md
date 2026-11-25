# Worked Example

From a real run on the course practice site (Toolshop product search, epic SCRUM-7, filed as SCRUM-42).

## Input

> The automated search test EX-36 failed: "a 500 must not look like 'no products'". Is this a real bug? If yes, write it up.

## 1. Reproduce and verdict

- Ran EX-36 twice (`--repeat-each=2`): the search API was mocked to return HTTP 500, and the page showed "0 products found for 'pliers'" and "There are no products found." both times. EX-37 (request aborted) did the same.
- A real, unmocked `PLIERS` search had returned **HTTP 500** once earlier the same day, with the same message on screen.

**Verdict: REPRODUCED (2 of 2), with one real-world sighting.**

## 2. App or test?

- The screenshot shows the no-results message, not a test error.
- The test waits for the search response before checking. It doesn't use a timer.
- Frontend bug: the API returned an error, and the page turned it into "no results".

## 3. Pattern

Any failed search request (500 or network failure) shows the same "no products found" message as a real empty result. The user can't tell "we don't sell this" from "search is broken".

## 4. Requirement

FR-05: *"When no product matches, the message 'There are no products found.' is shown."* The message is for "no match", not for errors. The error behaviour itself isn't specified, so "show an error message" is an assumption. Its impact is still clear.

## 5. Duplicates

Searched the project's bugs and the epic's children for "search", "500", "error", "no products". The only search bug was SCRUM-10 (short terms ignored), which is a different cause. So this one gets a **new ticket**.

## 6. The report

**Title:** `[Search] Server error or network failure is shown as "There are no products found."`

**Severity:** High (customers are told a product doesn't exist when search is actually broken; outages stay hidden)
**Priority:** High
**Breaks:** FR-05 (SCRUM-7)

### Environment
* URL: https://practicesoftwaretesting.com/ (frontend v2.5)
* Browser: Chromium (Playwright 1.65), macOS, guest
* Date: 2026-11-25, 14:56–15:00 UTC

### Steps to reproduce
1. Open the home page.
2. Make the search API fail. In the automated test, `/products/search` is **mocked** to return HTTP 500, or the request is aborted.
3. Type `pliers` and click **Search**.

### Expected result
An error message such as "Search is not available, please try again". **Not** a no-results message.

### Actual result
"Searched for: pliers", "0 products found for 'pliers'", "There are no products found."

### Likely cause / notes
The frontend treats any failed search response like an empty result. Seen without mocking once: a real `PLIERS` search got HTTP 500 at about 14:00 UTC.

### Reproducibility
Always with a failing API: 2 of 2 automated runs (EX-36 = 500, EX-37 = network failure).

### Evidence
`EX-36-server-500.png`, `ac02-PLIERS-no-results.png`.

## 7. Filing

The user said yes. One ticket was filed first and its parent, labels and priority were checked, then the other six. All seven keys were confirmed with a JQL search and shared as links.

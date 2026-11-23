# Fetching a posting that won't load

A failed fetch is not a missing posting. Before giving up, in order:

1. **403 from WebFetch:** usually the site's firewall rejecting the
   client, not the page being gone. Check `<origin>/robots.txt`; if it
   disallows the path for `*` or `Claude-User`, skip to step 3. Otherwise
   retry with curl and browser headers into the scratchpad, then strip tags:
   ```bash
   curl -sSL --compressed --max-time 45 -o page.html -w "HTTP %{http_code}\n" \
     -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36' \
     -H 'Accept: text/html,application/xhtml+xml;q=0.9,*/*;q=0.8' \
     -H 'Accept-Language: en-US,en;q=0.9' '<URL>'
   ```
   Greenhouse, Lever, and Ashby also serve the JD from their public job-board
   APIs, which beat scraping the page:
   - **Greenhouse:** `https://boards-api.greenhouse.io/v1/boards/<board_token>/jobs/<job_id>`
   - **Lever:** `https://api.lever.co/v0/postings/<company>/<job_id>`
   - **Ashby:** `https://api.ashbyhq.com/posting-api/job-board/<company>`
   A JS-rendered page the curl copy can't read goes to the browser tool if
   available.
2. **Login wall** (LinkedIn returns 200 with a sign-in page) or a
   **truncated aggregator listing:** headers won't fix it. Go to step 3.
3. **Search for the employer's own careers posting** by company and title.
   It is the better source anyway: aggregators drop the level, the team
   paragraph, and the full required/preferred split. Note any material
   difference between the two versions to the user rather than silently
   picking one.
4. Only after steps 1 to 3 fail, say the posting couldn't be retrieved and
   ask for the text. A real 404 or a "no longer accepting applications"
   page stops here too.

A fetch whose content doesn't match the expected company and title (a
listing page, a different req) is a failed fetch, not posting text.

# Tony's Suricata sid Checker

I have often found myself looking at Suricata logs via a siem or some other manner and not having access to the actual rule/signature. I also, wanted a way to pivot from the siem by clicking on a field and show the rule. This web app is a resource to do both. You can self host or use my public one.

This web app is a simple Flask app that will take a SID as input and search a local database for the rule.

It's ugly but it works.

### NOTES:
- This is statically pulling `https://rules.emergingthreats.net/open/suricata-5.0/emerging-all.rules.zip`
- This is basic raw HTML, no styling, should be fast

### The Future
I hope to add some styling as long as it doesn't effect performance.
I hope to expand the search feature to include other variables from the rules/sigs.
I hope to make the embedded reference active links.

### Why?
I had an idea if this was even possible with my limited and rudamentary python experience, so I gave it a try and it worked. It took nearly all day but I learned alot.

I hope others will point out my errors, or ways to improve.

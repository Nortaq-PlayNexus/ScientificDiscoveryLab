# PLAIN ENGLISH SUMMARY — EXP-0003 (vortex density in random light)

## What we asked

When light is scrambled into a random pattern (like laser speckle), its brightness
goes to zero at scattered points where the light's phase swirls around - "optical
vortices". Physicists have a formula (from Nye, Berry and the Kac-Rice theory) for
how many of these swirls you should find per unit area. We checked whether a
carefully built computer measurement reproduces that formula - and, importantly,
whether our swirl-counter itself can be trusted.

## What we did

We generated many random light fields in the computer with well-controlled
"waviness" (how fine the pattern is), counted the swirls in the middle of each field
(away from the edges), and compared the count with the formula. We used two
completely different counting methods, moved the pattern by half a pixel to check the
count didn't jump, scaled the brightness, re-ran with different random seeds, and
rebuilt everything a second way (summing many simple waves instead of using the fast
Fourier method) as an independent check.

## What we found

- For patterns fine enough to be well resolved (at least 8 pixels per wave), the
  measured swirl density matched the formula to within about 0.5% (all results
  between 0.995 and 1.006 of the prediction).
- Swirls always came in equal numbers of clockwise and anticlockwise (balanced to
  better than 0.3%).
- Moving the pattern by half a pixel changed the count by at most ~2% - the counter
  is not "grid-locked". This matters because the project this lab grew out of once
  had a counter that jumped from 48 to 218 on a small shift; we specifically built
  and tested against that failure.
- When the pattern contains a lot of very fine detail (close to the smallest feature
  the pixel grid can represent), both counters under-count: at the finest setting we
  measured about 0.83 of the prediction. We traced this to under-resolved fine
  detail, not to new physics, and mapped exactly where the counter becomes
  unreliable.
- The independent rebuild (summing simple waves, with its own counter) agreed to
  within about 2-3%.

## What this proves - and what it does not

It proves the lab can reproduce a known law with a trustworthy, artifact-aware
instrument, and it documents the limits of that instrument. It does **not** prove
anything new about nature: the formula is well known (it is a textbook result from
the 1970s-2000s). "The measured number of light swirls matches the standard formula"
is a calibration result, not a discovery.

## Why it is useful

Any later optics experiment in this lab that involves random or speckled light
(propagation, turbulence, phase retrieval) needs a swirl-counter it can trust. This
experiment certifies one, states the safe operating range (at least 8 pixels per
wave), and flags exactly where it fails.

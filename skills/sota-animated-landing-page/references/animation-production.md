# Animation production workflow

Use these settings as a baseline. Verify provider access and available modes before generating assets.

## 1. Visual direction

Match the exact concept and references. Define start, transition, and final composition before generating. Lock camera, framing, lighting, subject identity, and safe areas for HTML copy. For established characters, use verified references and inspect identity throughout the result.

## 2. Keyframes: Google Flow / Nano Banana Pro

- Open https://labs.google/fx/tools/flow.
- Image mode, Nano Banana Pro, 16:9, four variations.
- Upload references; generate the target scene first.
- Select the strongest end composition, upscale to 2K, download `end_frame.png`.
- Use **Add to prompt** on that end frame. Generate `start_frame.png` by removing foreground elements for a clean ambient reveal, or by creating the user's specified initial state.
- Preserve camera angle and lighting; upscale the start to 2K.

A manga project can use an editorial panel reveal with paper, ink, and authentic artwork. Other projects retain their own subject and style.

## 3. Transition: Google Flow / Veo 3.1 Quality

- Video mode, 16:9, two variations, Veo 3.1 Quality.
- Upload `start_frame.png` as Start Frame and `end_frame.png` as End Frame.
- Request an eight-second cinematic transition.
- Download the strongest clip in 1080p or 4K as `hero_transition.mp4`.
- Inspect intermediate frames for morphing, face drift, incorrect costumes, altered logos, unwanted text, flicker, and camera jumps. Keep actual typography in HTML.

This reveal is not inherently a loop: a different start and end are intentional.

## 4. Extract 30 FPS frames

Extract the interval from 1 to 8 seconds.

```sh
mkdir -p public/frames
ffmpeg -ss 00:00:01 -to 00:00:08 -i hero_transition.mp4 \
  -vf "fps=30,scale=1920:-1" -qscale:v 2 public/frames/frame_%04d.jpg
```

The same command with an explicit duration.

```sh
ffmpeg -ss 1 -i hero_transition.mp4 -t 7 \
  -vf "fps=30,scale=1920:-1" -q:v 2 public/frames/frame_%04d.jpg
```

Expect about 210 frames if the source contains the full interval. Verify count, dimensions, first/last frames, and duration rather than hardcoding an unverified total. Preserve master JPGs; generate delivery derivatives after measuring costs.

If FFmpeg is unavailable, use [Ezgif's video-to-JPG converter](https://ezgif.com/video-to-jpg). Select 1s–8s at 30 FPS, convert to JPG, then extract the downloaded ZIP to `public/frames/`.

## 5. Full UI: Google Stitch 3.1

- Use a connected Stitch MCP or browser at https://stitch.withgoogle.com.
- Web mode, Model 3.1 if available.
- Upload the End Frame/reference; generate the complete multi-section page matching its palette and typography.
- Iterate and export `code.html` and `screen.png`.
- Report unavailable modes/models; attribute exports to the tool that actually made them.

## 6. Code assembly

- Build a `400vh` scroll track containing a sticky `100vh` canvas.
- Load `public/frames/frame_0001.jpg` onward using the project's public URL convention.
- Prefetch compressed frames progressively; bound the decoded cache. Show a poster until ready; draw the nearest available frame if decoding lags.
- Normalize over the track's scrollable distance, clamp 0–1, and map to `Math.round(progress * (frameCount - 1))`.
- Schedule one animation frame per update; repaint only when frame/size changes. Respect pixel ratio without unbounded render size.
- Remove Stitch's static navbar and hero. Append lower sections below the animation.
- Use the selected font for the HTML headline/subheadline; fade smoothly beyond 30% hero progress.
- Add a fixed transparent glass navbar with `backdrop-filter: blur(12px)` and anchor links, with readable contrast. Avoid duplicate navbars and obscured anchor headings.
- Reduced motion: final frame, full headline, normal document flow. Mobile: direct access without prolonged mandatory scrolling.

## Ambient dashboard loops

Prepare these separately:

- Choose authentic title-matched footage with a locked camera and naturally repeatable motion, or source-authorized cyclic animation around verified artwork.
- Prefer a stable 6–10 second shot without cuts, subtitles, black fades, or dialogue dependence.
- Match position, movement direction, and lighting at the seam. Crossfade only compatible frames: a dissolve can create double faces. Reversal can make walking/smoke unnatural.
- Use the documented [FFmpeg xfade filter](https://ffmpeg.org/ffmpeg-filters.html#xfade) for an appropriate overlap, trim, then recheck the output boundary. A filter alone does not establish seamlessness.
- Deliver muted H.264 MP4 (`yuv420p`, fast-start), optionally WebM, plus a static poster.
- Use muted inline playback; handle autoplay rejection, pause offscreen/hidden-tab media, and expose pause. Do not load videos on every catalog tile.
- Observe three consecutive loops on Chrome, Safari, and mobile or representative browsers. Check no blank frame, freeze, flash, identity change, or obvious double image. Record status per title.
- Keep loops pending until evidence exists. Never substitute another series' footage to complete a count.

## 7. Preview and deployment

Serve locally, verify scrubbing, layouts, links, and responsive/reduced-motion states. Use GitHub and Vercel when requested. Keep unavailable providers, missing media, and unfinished checks explicit.

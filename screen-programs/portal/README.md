# Portal

Hold both hands up and make a frame from the two thumb tips and the
two pinky tips. The camera image inside that frame is
perspective-warped flat and run through a filter, live — the frame
is a little window you carry around the room.

- **10 filters.** Touch a fingertip of one hand to a fingertip of the
  other to step to the next, or jump with keys 1–9, 0.
- **F** toggles fullscreen. **Q** quits.

The concept follows @byte0880's "RETROLENS" demo on TikTok — the
two-hand frame and the fingertip-touch switching are theirs; the
implementation here is mine.

```sh
python3 portal.py --camera 1
```

(Started from the shared environment — see `demo/PROGRAMS.md` in the
repo root for the full routine.)

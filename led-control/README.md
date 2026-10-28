# led-control/ — the physical projects

Two projects where the gestures (or the program) end in real light,
both on the same Arduino Uno + breadboard rig the repo started with.

| Project | Folder | What it is |
|---------|--------|------------|
| Finger LEDs | `finger-leds/` | Camera counts fingers → serial → Uno lights that many of five plain LEDs. The first build; the shared Python environment and hand model live with this project. |
| Moon Flowers | `moon-flowers/` | Two RGB LEDs in tissue diffusers on gooseneck stems. Left alone, they breathe through a colour cycle on the Uno; raise both hands and they become an instrument you conduct. |

Both projects speak the same serial habits — short text commands at
9600 baud, echoed by the sketch — which is how each link was
debugged.

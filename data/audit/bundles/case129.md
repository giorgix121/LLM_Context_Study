# case129: home-assistant/core bb77af71ff81

File: `homeassistant/components/stream/recorder.py` · committed 2022-09-06 20:30:55-01:00 · SZZ label: RISKY

## Commit message

```
Use fragmented mp4 in stream recorder (#77822)
```

## Diff of the target file

```diff
@@ -104,7 +104,11 @@ class RecorderOutput(StreamOutput):
                     "w",
                     format=RECORDER_CONTAINER_FORMAT,
                     container_options={
-                        "video_track_timescale": str(int(1 / source_v.time_base))
+                        "video_track_timescale": str(int(1 / source_v.time_base)),
+                        "movflags": "frag_keyframe",
+                        "min_frag_duration": str(
+                            self.stream_settings.min_segment_duration
+                        ),
                     },
                 )
```

## Lines SZZ blamed (line numbers in the new version)

```
  107                          "video_track_timescale": str(int(1 / source_v.time_base)),
  108                          "movflags": "frag_keyframe",
  109                          "min_frag_duration": str(
  110                              self.stream_settings.min_segment_duration
  111                          ),
```

## Candidate fixes (1 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

### Candidate 1: 3b78df07dec8 (2022-10-21)

Message:

```
Use empty_moov in stream recorder (#80726)
```

Removed blamed lines: `"movflags": "frag_keyframe",`

Patch of this file:

```diff
@@ -106,7 +106,7 @@ def write_segment(segment: Segment) -> None:
                     format=RECORDER_CONTAINER_FORMAT,
                     container_options={
                         "video_track_timescale": str(int(1 / source_v.time_base)),
-                        "movflags": "frag_keyframe",
+                        "movflags": "frag_keyframe+empty_moov",
                         "min_frag_duration": str(
                             self.stream_settings.min_segment_duration
                         ),
```

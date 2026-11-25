# case129: home-assistant/core bb77af71ff81

Sampled file (the only file the models saw): `homeassistant/components/stream/recorder.py` · committed 2022-09-06 20:30:55-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Use fragmented mp4 in stream recorder (#77822)
```

## Diff of the sampled file

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

## Other files changed by this commit (0)

(none)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 3b78df07dec8 (2022-10-21) · pull request #80726: Use empty_moov in stream recorder

Pull-request labels: Hacktoberfest, core, cla-signed, small-pr, integration: stream, by-code-owner, bugfix, Quality Scale: internal

Commit message:

```
Use empty_moov in stream recorder (#80726)
```

Pull-request description:

```
## Proposed change
<!--
  Describe the big picture of your changes here to communicate to the
  maintainers why we should accept this pull request. If it fixes a bug
  or resolves a feature request, be sure to link to that issue in the
  additional information section.
-->

https://github.com/home-assistant/core/pull/77822 changed the stream recorder to use fragmented mp4s. However, some players have issues playing back fragmented mp4s, and the issues are particularly noticeable when the file does not have an empty moov atom.
This PR keeps the stream recorder output as fragmented mp4, but it uses the empty_moov flag to ensure that the output is 100% fragmented. This should improve compatibility with some players.

## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple boxes to be checked, you'll most likely need to
  split it into multiple PRs. This makes things easier and faster to code review.
-->

- [ ] Dependency upgrade
- [x] Bugfix (non-breaking change which fixes an issue)
- [ ] New integration (thank you!)
- [ ] New feature (which adds functionality to an existing integration)
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: `"movflags": "frag_keyframe",`
- in other files of the commit: none

Patch of the sampled file in this fix:

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

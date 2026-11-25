# case144: getsentry/sentry 832933fc29ef

File: `src/sentry/utils/settings.py` · committed 2022-11-01 18:55:47-01:00 · SZZ label: RISKY

## Commit message

```
feat(session-replay): adds banner for session replay waitlist (#40797)

This PR adds a banner to the logic page to show a banner with a link to
join the waitlist for Session Replay. Note that we purposely don't show
this to self-hosted users.

<img width="1023" alt="Screen Shot 2022-10-31 at 10 36 05 PM"
src="https://user-images.githubusercontent.com/8533851/199115003-ebfe7a72-40ab-4784-b541-c74e91a2b981.png">

I added a CSS style to hide the banner if the screen is so narrow that
it wouldn't fit on one line.
```

## Diff of the target file

```diff
@@ -52,3 +52,9 @@ def is_self_hosted():
         return settings.SENTRY_SELF_HOSTED
     except AttributeError:
         return settings.SENTRY_ONPREMISE
+
+
+def is_saas():
+    from django.conf import settings
+
+    return settings.SENTRY_IS_SAAS
```

## Lines SZZ blamed (line numbers in the new version)

```
   55  
   56  
   57  def is_saas():
   58      from django.conf import settings
   59  
   60      return settings.SENTRY_IS_SAAS
```

## Candidate fixes (1 later commits to this file remove a blamed line; 2 later commits up to 2023-06-30 checked)

### Candidate 1: 38bee5babc36 (2022-11-01)

Message:

```
fix(backend): session replay banner setting (#40847)

Remove saas flag
```

Removed blamed lines: `def is_saas():`; `from django.conf import settings`; `return settings.SENTRY_IS_SAAS`

Patch of this file:

```diff
@@ -52,9 +52,3 @@ def is_self_hosted():
         return settings.SENTRY_SELF_HOSTED
     except AttributeError:
         return settings.SENTRY_ONPREMISE
-
-
-def is_saas():
-    from django.conf import settings
-
-    return settings.SENTRY_IS_SAAS
```

# case144: getsentry/sentry 832933fc29ef

Sampled file (the only file the models saw): `src/sentry/utils/settings.py` · committed 2022-11-01 18:55:47-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

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

## Other files changed by this commit (3)

- `src/sentry/conf/server.py` (+3 −0)
- `src/sentry/templates/sentry/layout.html` (+45 −1)
- `src/sentry/web/frontend/auth_login.py` (+3 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 38bee5babc36 (2022-11-01) · pull request #40847: fix(backend): session replay banner setting

Pull-request labels: Scope: Backend

Commit message:

```
fix(backend): session replay banner setting (#40847)

Remove saas flag
```

Pull-request description:

```
Remove saas flag
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: `def is_saas():`; `from django.conf import settings`; `return settings.SENTRY_IS_SAAS`
- in `src/sentry/conf/server.py`: `SENTRY_IS_SAAS = False`
- in `src/sentry/web/frontend/auth_login.py`: `"show_session_replay_banner": is_saas(),`; `from sentry.utils.settings import is_saas`

Patch of the sampled file in this fix:

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

Patch of `src/sentry/conf/server.py` in this fix:

```diff
@@ -2888,5 +2888,5 @@ def build_cdc_postgres_init_db_volume(settings):
 # to a slice ID
 SENTRY_SLICING_CONFIG: Mapping[str, Mapping[Tuple[int, int], int]] = {}
 
-# Flag if we are in SaaS mode
-SENTRY_IS_SAAS = False
+# Show session replay banner on login page
+SHOW_SESSION_REPLAY_BANNER = False
```

Patch of `src/sentry/web/frontend/auth_login.py` in this fix:

```diff
@@ -28,7 +28,6 @@
 )
 from sentry.utils.client_state import get_client_state_redirect_uri
 from sentry.utils.sdk import capture_exception
-from sentry.utils.settings import is_saas
 from sentry.utils.urls import add_params_to_url
 from sentry.web.forms.accounts import AuthenticationForm, RegistrationForm
 from sentry.web.frontend.base import BaseView
@@ -263,7 +262,7 @@ def handle_basic_auth(self, request: Request, **kwargs):
             "register_form": register_form,
             "CAN_REGISTER": can_register,
             "join_request_link": self.get_join_request_link(organization),
-            "show_session_replay_banner": is_saas(),
+            "show_session_replay_banner": settings.SHOW_SESSION_REPLAY_BANNER,
         }
 
         context.update(additional_context.run_callbacks(request))
```

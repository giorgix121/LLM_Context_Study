# case010: home-assistant/core d0ac1073a0f4

Sampled file (the only file the models saw): `homeassistant/components/pushover/__init__.py` · committed 2022-09-29 13:40:53-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Allow entries with same user_key for Pushover (#77904)

* Allow entries with same user_key for Pushover

* remove unique_id completely

* Abort reauth if entered api_key already exists
Update tests
```

## Diff of the sampled file

```diff
@@ -25,6 +25,10 @@ async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
 async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
     """Set up pushover from a config entry."""
 
+    # remove unique_id for beta users
+    if entry.unique_id is not None:
+        hass.config_entries.async_update_entry(entry, unique_id=None)
+
     pushover_api = PushoverAPI(entry.data[CONF_API_KEY])
     try:
         await hass.async_add_executor_job(
```

## Other files changed by this commit (3)

- `homeassistant/components/pushover/config_flow.py` (+12 −2)
- `tests/components/pushover/test_config_flow.py` (+45 −6)
- `tests/components/pushover/test_init.py` (+10 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 3aa24afad860 (2022-10-21) · pull request #80602: Retry setup in case of empty response from Pushover api

Pull-request labels: Hacktoberfest, cla-signed, small-pr, integration: pushover, has-tests, by-code-owner, bugfix, Quality Scale: No score

Commit message:

```
Retry setup in case of empty response from Pushover api (#80602)

Retry setup in case of empty response
```

Pull-request description:

```
<!--
  You are amazing! Thanks for contributing to our project!
  Please, DO NOT DELETE ANY TEXT from this template! (unless instructed).
-->
## Breaking change
<!--
  If your PR contains a breaking change for existing users, it is important
  to tell them what breaks, how to make it work again and why we did this.
  This piece of text is published with the release notes, so it helps if you
  write it towards our users, not us.
  Note: Remove this section if this PR is NOT a breaking change.
-->


## Proposed change
<!--
  Describe the big picture of your changes here to communicate to the
  maintainers why we should accept this pull request. If it fixes a bug
  or resolves a feature request, be sure to link to that issue in the
  additional information section.
-->
Catch `ValueError` exception and retry setup. Should fix issue #79957

## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple boxes to be checked, you'll most likely need to
  split it into multiple PRs. This makes things easier and faster to code review.
-->

- [ ] Dependency upgrade
- [x] Bugfix (non-breaking change which
[... cut ...]
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix changes this file, but not lines the commit added)
- in `tests/components/pushover/test_init.py`: `async def test_unique_id_updated(hass: HomeAssistant) -> None:`

Patch of the sampled file in this fix:

```diff
@@ -35,7 +35,7 @@ async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
             pushover_api.validate, entry.data[CONF_USER_KEY]
         )
 
-    except BadAPIRequestError as err:
+    except (BadAPIRequestError, ValueError) as err:
         if "application token is invalid" in str(err):
             raise ConfigEntryAuthFailed(err) from err
         raise ConfigEntryNotReady(err) from err
```

Patch of `tests/components/pushover/test_init.py` in this fix:

```diff
@@ -6,6 +6,7 @@
 import aiohttp
 from pushover_complete import BadAPIRequestError
 import pytest
+from requests_mock import Mocker
 
 from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
 from homeassistant.components.pushover.const import DOMAIN
@@ -19,7 +20,7 @@
 from tests.components.repairs import get_repairs
 
 
-@pytest.fixture(autouse=True)
+@pytest.fixture(autouse=False)
 def mock_pushover():
     """Mock pushover."""
     with patch(
@@ -33,6 +34,7 @@ async def test_setup(
     hass_ws_client: Callable[
         [HomeAssistant], Awaitable[aiohttp.ClientWebSocketResponse]
     ],
+    mock_pushover: MagicMock,
 ) -> None:
     """Test integration failed due to an error."""
     assert await async_setup_component(
@@ -56,7 +58,9 @@ async def test_setup(
     assert issues[0]["issue_id"] == "deprecated_yaml"
 
 
-async def test_async_setup_entry_success(hass: HomeAssistant) -> None:
+async def test_async_setup_entry_success(
+    hass: HomeAssistant, mock_pushover: MagicMock
+) -> None:
     """Test pushover successful setup."""
     entry = MockConfigEntry(
         domain=DOMAIN,
@@ -68,7 +72,7 @@ async def test_async_setup_entry_success(hass: HomeAssistant) -> None:
     assert entry.state == ConfigEntryState.LOADED
 
 
-async def test_unique_id_updated(hass: HomeAssistant) -> None:
+async def test_unique_id_updated(hass: HomeAssistant, mock_pushover: MagicMock) -> None:
     """Test updating unique_id to new format."""
     entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, unique_id="MYUSERKEY")
     entry.add_to_hass(hass)
@@ -106,3 +110,20 @@ async def test_async_setup_entry_failed_conn_error(
     await hass.config_entries.async_setup(entry.entry_id)
     await hass.async_block_till_done()
     assert entry.state == ConfigEntryState.SETUP_RETRY
+
+
+async def test_async_setup_entry_failed_json_error(
+    hass: HomeAssistant, requests_mock: Mocker
+) -> None:
+    """Test pushover failed setup due to bad json response from library."""
+    entry = MockConfigEntry(
+        domain=DOMAIN,
+        data=MOCK_CONFIG,
+    )
+    entry.add_to_hass(hass)
+    requests_mock.post(
+        "https://api.pushover.net/1/users/validate.js
[... cut ...]
```

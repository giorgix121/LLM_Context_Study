# case117: getsentry/sentry c1c0a777a4f9

Sampled file (the only file the models saw): `src/sentry/region_to_control/producer.py` · committed 2022-10-20 09:00:50-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
chore(hybrid-cloud): Adding service layer, starting with project key (#40294)

First cut at a hybrid cloud service abstraction. No backing
implementation for now, but includes a test to be replaced with
`RegionClient` call. Extracted from
https://github.com/getsentry/sentry/pull/40214
```

## Diff of the sampled file

```diff
@@ -68,7 +68,8 @@ def get_region_to_control_producer() -> KafkaProducer:
 
         @atexit.register
         def exit_handler():
-            _publisher.close()
+            if _publisher is not None:
+                _publisher.close()
 
     return _publisher
 
@@ -86,11 +87,5 @@ def clear_region_to_control_producer():
 
 
 def _should_produce_to_kafka():
-    from sentry import options
-
     mode = SiloMode.get_current_mode()
-    is_region = mode == SiloMode.REGION
-    is_mono_with_producer = mode == SiloMode.MONOLITH and options.get(
-        "hc.region-to-control.monolith-publish"
-    )
-    return is_region or is_mono_with_producer
+    return mode == SiloMode.REGION
```

## Other files changed by this commit (22)

- `src/sentry/api/endpoints/api_application_details.py` (+2 −2)
- `src/sentry/api/endpoints/integrations/sentry_apps/interaction.py` (+2 −2)
- `src/sentry/models/apiapplication.py` (+2 −2)
- `src/sentry/models/apikey.py` (+2 −2)
- `src/sentry/models/authenticator.py` (+2 −2)
- `src/sentry/models/authidentity.py` (+2 −2)
- `src/sentry/models/authprovider.py` (+3 −3)
- `src/sentry/models/avatars/user_avatar.py` (+2 −2)
- `src/sentry/models/options/user_option.py` (+2 −2)
- `src/sentry/models/scheduledeletion.py` (+2 −2)
- `src/sentry/models/userip.py` (+2 −7)
- `src/sentry/models/userpermission.py` (+2 −2)
- `src/sentry/models/userrole.py` (+3 −3)
- `src/sentry/options/defaults.py` (+0 −4)
- `src/sentry/services/hybrid_cloud/__init__.py` (+322 −0)
- `src/sentry/testutils/silo.py` (+1 −0)
- `src/sentry/web/client_config.py` (+6 −12)
- `tests/conftest.py` (+27 −0)
- `tests/sentry/api/endpoints/test_organization_details.py` (+1 −2)
- `tests/sentry/middleware/test_auth.py` (+3 −4)
- `tests/sentry/services/test_project_key_service.py` (+19 −0)
- `tests/sentry/web/frontend/test_error_404.py` (+2 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: b82fcb6119a4 (2022-11-02) · pull request #40862: chore(hybrid-cloud): mypy fixes and organization improvement

Pull-request labels: Scope: Backend

Commit message:

```
chore(hybrid-cloud): mypy fixes and organization improvement (#40862)

Moves organization and project_key services into separate directories,
adds hybrid cloud to mypy.
Part of a multi step extracting of
https://github.com/getsentry/sentry/pull/40772/files into pieces.
```

Pull-request description:

```
Moves organization and project_key services into separate directories, adds hybrid cloud to mypy.
Part of a multi step extracting of https://github.com/getsentry/sentry/pull/40772/files into pieces.
```

This fix changes 11 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/services/hybrid_cloud/__init__.py`: `)`; `) -> List[ApiOrganization]:`; `) -> Optional[ApiOrganization]:`; `):`; `:param only_visible:`; `:param scope:`
- in `src/sentry/web/client_config.py`: `from sentry.services.hybrid_cloud import ProjectKeyRole, project_key_service`
- in `tests/conftest.py`: `StubProjectKeyService,`; `from sentry.services.hybrid_cloud import (`; `project_key_service,`; `service_stubbed,`
- in `tests/sentry/services/test_project_key_service.py`: `from sentry.services.hybrid_cloud import project_key_service, use_real_service`

Patch of `src/sentry/services/hybrid_cloud/__init__.py` in this fix:

```diff
@@ -1,58 +1,16 @@
 import contextlib
 import logging
 from abc import ABC, abstractmethod
-from dataclasses import dataclass
-from enum import Enum
-from typing import Dict, Generic, Iterable, List, Mapping, Optional, Type, TypeVar, cast
-
-from sentry.models import Organization, OrganizationMember, OrganizationStatus
+from typing import Any, Callable, Dict, Generator, Generic, Mapping, Optional, Type, TypeVar, cast
 
 logger = logging.getLogger(__name__)
 
-from django.db.models import F
-
 from sentry.silo import SiloMode
 
 
-class ProjectKeyRole(Enum):
-    store = "store"
-    api = "api"
-
-    def as_orm_role(self):
-        from sentry.models import ProjectKey
-
-        if self == ProjectKeyRole.store:
-            return ProjectKey.roles.store
-        elif self == ProjectKeyRole.api:
-            return ProjectKey.roles.api
-        else:
-            raise ValueError("Unexpected project key role enum")
-
-
-@dataclass
-class ApiProjectKey:
-    dsn_public: str = ""
-
-
-@dataclass
-class ApiOrganizationMember:
-    # This can be null when the user is deleted.
-    user_id: Optional[int]
-    pass
-
-
-@dataclass
-class ApiOrganization:
-    slug: str = ""
-    id: int = -1
-    # exists iff the organization was queried with a user_id context, and that user_id
-    # was confirmed to be a member.
-    member: Optional[ApiOrganizationMember] = None
-
-
 class InterfaceWithLifecycle(ABC):
     @abstractmethod
-    def close(self):
+    def close(self) -> None:
         pass
 
 
@@ -70,15 +28,17 @@ class DelegatedBySiloMode(Generic[ServiceInterface]):
     service is closed, or when the backing service implementation changes.
     """
 
-    _constructors: Mapping[SiloMode, Type[ServiceInterface]]
+    _constructors: Mapping[SiloMode, Callable[[], ServiceInterface]]
     _singleton: Dict[SiloMode, ServiceInterface]
 
-    def __init__(self, mapping: Mapping[SiloMode, Type[ServiceInterface]]):
+    def __init__(self, mapping: Mapping[SiloMode, Callable[[], ServiceInterface]]):
         self._constructors = mapping
         self._singleton = {}
 
     @contextlib.contextmanager
-    def with_replacement(self, service: Optional[ServiceInterface], silo_mode:
[... cut ...]
```

Patch of `src/sentry/web/client_config.py` in this fix:

```diff
@@ -13,7 +13,7 @@
 from sentry.auth.access import get_cached_organization_member
 from sentry.auth.superuser import is_active_superuser
 from sentry.models import Organization, OrganizationMember
-from sentry.services.hybrid_cloud import ProjectKeyRole, project_key_service
+from sentry.services.hybrid_cloud.project_key import ProjectKeyRole, project_key_service
 from sentry.utils import auth
 from sentry.utils.assets import get_frontend_app_asset_url
 from sentry.utils.email import is_smtp_enabled
```

Patch of `tests/conftest.py` in this fix:

```diff
@@ -129,13 +129,12 @@ def setup_default_hybrid_cloud_stubs():
         MockRegionToControlMessageService,
         region_to_control_message_service,
     )
-    from sentry.services.hybrid_cloud import (
+    from sentry.services.hybrid_cloud import service_stubbed
+    from sentry.services.hybrid_cloud.organization import (
         StubOrganizationService,
-        StubProjectKeyService,
         organization_service,
-        project_key_service,
-        service_stubbed,
     )
+    from sentry.services.hybrid_cloud.project_key import StubProjectKeyService, project_key_service
     from sentry.silo import SiloMode
 
     stubs = [
```

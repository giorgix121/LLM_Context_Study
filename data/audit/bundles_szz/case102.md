# case102: getsentry/sentry a882713d1b8f

Sampled file (the only file the models saw): `src/sentry/web/frontend/home.py` · committed 2022-10-26 02:03:31-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
chore(hybrid-cloud): Refactor Organization ORM out of views and auth (#40362)

For hybrid cloud, the organization and related models will not exist in the control silo, but will be necessary for certain auth related flows.  This change is the first of many to make the core auth flows compatible with a split silo world by introducing a service object that captures existing needs for an organization arond the `get_active_organization` method.  Behavior should remain identical, except that the pure ORM object is not available in many places.  Those places have been updated to use a new thinner model object that corresponds with future control silo's data availability.

Co-authored-by: getsantry[bot] <66042841+getsantry[bot]@users.noreply.github.com>
```

## Diff of the sampled file

```diff
@@ -10,9 +10,8 @@ from sentry.web.frontend.base import BaseView
 class HomeView(BaseView):
     def get(self, request: Request) -> Response:
         # If the active organization has an ongoing onboarding session, redirect to onboarding
-        organization = self.get_active_organization(request)
-        if organization:
-            redirect_uri = get_client_state_redirect_uri(organization.slug, None)
+        if self.active_organization:
+            redirect_uri = get_client_state_redirect_uri(self.active_organization.slug, None)
             if redirect_uri and is_valid_redirect(
                 redirect_uri, allowed_hosts=(request.get_host(),)
             ):
```

## Other files changed by this commit (16)

- `src/sentry/api/endpoints/auth_config.py` (+5 −2)
- `src/sentry/api/endpoints/auth_login.py` (+11 −3)
- `src/sentry/api/serializers/models/auth_provider.py` (+2 −2)
- `src/sentry/integrations/github/integration.py` (+11 −9)
- `src/sentry/models/lostpasswordhash.py` (+2 −2)
- `src/sentry/models/organization.py` (+5 −3)
- `src/sentry/models/user.py` (+2 −2)
- `src/sentry/services/hybrid_cloud/__init__.py` (+65 −16)
- `src/sentry/utils/auth.py` (+4 −3)
- `src/sentry/web/frontend/auth_login.py` (+28 −18)
- `src/sentry/web/frontend/base.py` (+116 −98)
- `src/sentry/web/frontend/js_sdk_loader.py` (+7 −0)
- `src/sentry/web/frontend/organization_auth_settings.py` (+3 −3)
- `src/sentry/web/frontend/restore_organization.py` (+13 −10)
- `tests/integration/test_sso.py` (+14 −13)
- `tests/sentry/web/frontend/test_auth_login.py` (+1 −1)

## Fix commits that the dataset links to this commit (2)

### Fix 1: 945e7236db55 (2022-10-31) · pull request #40809: fix(restore): Organization restore endpoint should not bork if the org no longer exists

Pull-request labels: Scope: Backend

Commit message:

```
fix(restore): Organization restore endpoint should not bork if the org no longer exists (#40809)
```

Pull-request description:

```
Fixes SENTRY-WCD
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/web/frontend/restore_organization.py`: `if organization.member:`

Patch of `src/sentry/web/frontend/restore_organization.py` in this fix:

```diff
@@ -37,7 +37,7 @@ def determine_active_organization(self, request: Request, organization_slug=None
         organization = organization_service.get_organization_by_slug(
             user_id=request.user.id, slug=organization_slug, only_visible=False, allow_stale=False
         )
-        if organization.member:
+        if organization and organization.member:
             self.active_organization = organization
         else:
             self.active_organization = None
```

### Fix 2: b82fcb6119a4 (2022-11-02) · pull request #40862: chore(hybrid-cloud): mypy fixes and organization improvement

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
- in `src/sentry/services/hybrid_cloud/__init__.py`: `) -> ApiOrganization:`; `) -> List[Organization]:`; `) -> Optional[ApiOrganizationMember]:`; `@abstractmethod`; `@dataclass`; `Used to look up an organization membership by an email, used in very specific edge cases.`
- in `src/sentry/utils/auth.py`: `from sentry.services.hybrid_cloud import ApiOrganization`
- in `src/sentry/web/frontend/auth_login.py`: `from sentry.services.hybrid_cloud import organization_service`
- in `src/sentry/web/frontend/base.py`: `from sentry.services.hybrid_cloud import ApiOrganization, organization_service`
- in `src/sentry/web/frontend/restore_organization.py`: `from sentry.services.hybrid_cloud import organization_service`

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

Patch of `src/sentry/utils/auth.py` in this fix:

```diff
@@ -16,7 +16,7 @@
 from rest_framework.request import Request
 
 from sentry.models import Authenticator, Organization, User
-from sentry.services.hybrid_cloud import ApiOrganization
+from sentry.services.hybrid_cloud.organization import ApiOrganization
 from sentry.utils import metrics
 from sentry.utils.http import absolute_uri
```

Patch of `src/sentry/web/frontend/auth_login.py` in this fix:

```diff
@@ -16,7 +16,7 @@
 from sentry.constants import WARN_SESSION_EXPIRED
 from sentry.http import get_server_hostname
 from sentry.models import AuthProvider, Organization, OrganizationMember, OrganizationStatus
-from sentry.services.hybrid_cloud import organization_service
+from sentry.services.hybrid_cloud.organization import organization_service
 from sentry.signals import join_request_link_viewed, user_signup
 from sentry.utils import auth, json, metrics
 from sentry.utils.auth import (
```

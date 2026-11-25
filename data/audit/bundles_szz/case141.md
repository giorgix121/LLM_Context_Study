# case141: getsentry/sentry 5cd890d8f700

Sampled file (the only file the models saw): `src/sentry/discover/endpoints/discover_saved_queries.py` · committed 2022-09-27 04:18:35-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat(discover): Add discover homepage query endpoint (#39153)

Adds `/api/0/:org-id/discover/homepage/` as a private endpoint. This
endpoint supports GET, PUT, and DELETE
```

## Diff of the sampled file

```diff
@@ -35,7 +35,7 @@ class DiscoverSavedQueriesEndpoint(OrganizationEndpoint):
             .select_related("created_by")
             .prefetch_related("projects")
             .extra(select={"lower_name": "lower(name)"})
-        )
+        ).exclude(is_homepage=True)
         query = request.query_params.get("query")
         if query:
             tokens = tokenize_query(query)
```

## Other files changed by this commit (4)

- `src/sentry/api/urls.py` (+6 −0)
- `src/sentry/discover/endpoints/discover_homepage_query.py` (+107 −0)
- `tests/snuba/api/endpoints/test_discover_homepage_query.py` (+112 −0)
- `tests/snuba/api/endpoints/test_discover_saved_queries.py` (+20 −0)

## Fix commits that the dataset links to this commit (4)

### Fix 1: 3554a36b4a4c (2022-10-06) · pull request #39762: fix(discover-home-page): Saved name field as an empty string during p…

Pull-request labels: Scope: Backend

Commit message:

```
fix(discover-home-page): Saved name field as an empty string during p… (#39762)

Note: Removed name check from other tests, now that it has a test
dedicated to it.

Co-authored-by: Abdullah Khan <abdullahkhan@P40P69L0VQ-Abdullah-Khan.local>
```

Pull-request description:

```
Note: Removed name check from other tests, now that it has a test dedicated to it.
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/discover/endpoints/discover_homepage_query.py`: `name=data["name"],`
- in `tests/snuba/api/endpoints/test_discover_homepage_query.py`: `assert new_query.name == homepage_query_payload["name"]`; `assert saved_query.name == "A new homepage query update"`

Patch of `src/sentry/discover/endpoints/discover_homepage_query.py` in this fix:

```diff
@@ -75,7 +75,7 @@ def put(self, request: Request, organization) -> Response:
         if previous_homepage:
             previous_homepage.update(
                 organization=organization,
-                name=data["name"],
+                name="",
                 query=data["query"],
                 version=data["version"],
             )
@@ -84,7 +84,7 @@ def put(self, request: Request, organization) -> Response:
 
         model = DiscoverSavedQuery.objects.create(
             organization=organization,
-            name=data["name"],
+            name="",
             query=data["query"],
             version=data["version"],
             created_by=request.user,
```

Patch of `tests/snuba/api/endpoints/test_discover_homepage_query.py` in this fix:

```diff
@@ -60,7 +60,6 @@ def test_put_updates_existing_homepage_query_to_reflect_new_data(self):
 
         saved_query.refresh_from_db()
         assert response.data == serialize(saved_query)
-        assert saved_query.name == "A new homepage query update"
         assert saved_query.query["fields"] == ["field1", "field2"]
         assert set(saved_query.projects.values_list("id", flat=True)) == set(self.project_ids)
 
@@ -83,11 +82,31 @@ def test_put_creates_new_discover_saved_query_if_none_exists(self):
             created_by=self.user, organization=self.org, is_homepage=True
         )
         assert response.data == serialize(new_query)
-        assert new_query.name == homepage_query_payload["name"]
         assert new_query.query["fields"] == homepage_query_payload["fields"]
         assert new_query.query["environment"] == homepage_query_payload["environment"]
         assert set(new_query.projects.values_list("id", flat=True)) == set(self.project_ids)
 
+    def test_put_responds_with_saved_empty_name_field(self):
+        homepage_query_payload = {
+            "version": 2,
+            "name": "New Homepage Query",
+            "projects": self.project_ids,
+            "environment": ["alpha"],
+            "fields": ["environment", "platform.name"],
+            "orderby": "-timestamp",
+            "range": None,
+        }
+        with self.feature(FEATURES):
+            response = self.client.put(self.url, data=homepage_query_payload)
+
+        assert response.status_code == 201, response.content
+
+        new_query = DiscoverSavedQuery.objects.get(
+            created_by=self.user, organization=self.org, is_homepage=True
+        )
+        assert new_query.name == ""
+        assert response.data["name"] == ""
+
     def test_post_not_allowed(self):
         homepage_query_payload = {
             "version": 2,
```

### Fix 2: 47f7aa778941 (2022-10-07) · pull request #39793: fix(discover-homepage): Saving from homepage fails

Pull-request labels: Scope: Backend

Commit message:

```
fix(discover-homepage): Saving from homepage fails (#39793)

Saving from the homepage fails because it sends along name as an empty
string. The DiscoverSavedQuerySerializer expects a name so we can
temporarily set one for the purposes of bypassing this condition
```

Pull-request description:

```
Saving from the homepage fails because it sends along name as an empty string. The DiscoverSavedQuerySerializer expects a name so we can temporarily set one for the purposes of bypassing this condition
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/discover/endpoints/discover_homepage_query.py`: `data=request.data,`

Patch of `src/sentry/discover/endpoints/discover_homepage_query.py` in this fix:

```diff
@@ -65,7 +65,8 @@ def put(self, request: Request, organization) -> Response:
             raise ParseError(detail="No Projects found, join a Team")
 
         serializer = DiscoverSavedQuerySerializer(
-            data=request.data,
+            # HACK: To ensure serializer data is valid, pass along a name temporarily
+            data={**request.data, "name": "New Query"},
             context={"params": params},
         )
         if not serializer.is_valid():
```

### Fix 3: 6c062c1a1f53 (2022-10-11) · pull request #39882: fix(discover-homepage): Remove feature flag check on homepage endpoint

Pull-request labels: Scope: Backend

Commit message:

```
fix(discover-homepage): Remove feature flag check on homepage endpoint (#39882)

Removes the `discover-query-builder-as-landing-page` feature flag check
because instability in flagr may cause the whole homepage view to error.
Removing this check shouldn't be too impactful because the functionality
is still flagged by discover-query and the user can only act on a single
instance of a homepage query
```

Pull-request description:

```
Removes the `discover-query-builder-as-landing-page` feature flag check because instability in flagr may cause the whole homepage view to error. Removing this check shouldn't be too impactful because the functionality is still flagged by discover-query and the user can only act on a single instance of a homepage query
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/discover/endpoints/discover_homepage_query.py`: `"organizations:discover-query-builder-as-landing-page", organization, actor=request.user`; `)`; `) and features.has(`; `features.has("organizations:discover", organization, actor=request.user)`; `or features.has("organizations:discover-query", organization, actor=request.user)`; `return (`

Patch of `src/sentry/discover/endpoints/discover_homepage_query.py` in this fix:

```diff
@@ -30,12 +30,9 @@ class DiscoverHomepageQueryEndpoint(OrganizationEndpoint):
     )
 
     def has_feature(self, organization, request):
-        return (
-            features.has("organizations:discover", organization, actor=request.user)
-            or features.has("organizations:discover-query", organization, actor=request.user)
-        ) and features.has(
-            "organizations:discover-query-builder-as-landing-page", organization, actor=request.user
-        )
+        return features.has(
+            "organizations:discover", organization, actor=request.user
+        ) or features.has("organizations:discover-query", organization, actor=request.user)
 
     def get(self, request: Request, organization) -> Response:
         if not self.has_feature(organization, request):
```

### Fix 4: 779421cbce85 (2022-10-04) · pull request #39604: fix(discover-homepage): Project IDs not saving on update

Pull-request labels: Scope: Backend

Commit message:

```
fix(discover-homepage): Project IDs not saving on update (#39604)

Project IDs were being properly set when the PUT triggered a create, but
not when a previously created query was being updated. This is because
the relationship is a M2M field and the projects need to be explicitly
added.

I used a set to compare project IDs in the response because order
doesn't really matter for us and I wanted to avoid any potential flakes
due to this.
```

Pull-request description:

```
Project IDs were being properly set when the PUT triggered a create, but not when a previously created query was being updated. This is because the relationship is a M2M field and the projects need to be explicitly added.

I used a set to compare project IDs in the response because order doesn't really matter for us and I wanted to avoid any potential flakes due to this.
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/snuba/api/endpoints/test_discover_homepage_query.py`: `"projects": ["-1"],`

Patch of `tests/snuba/api/endpoints/test_discover_homepage_query.py` in this fix:

```diff
@@ -12,6 +12,10 @@ def setUp(self):
         super().setUp()
         self.url = reverse("sentry-api-0-discover-homepage-query", args=[self.org.slug])
         self.query = {"fields": ["test"], "conditions": [], "limit": 10}
+        self.project_ids = [
+            self.create_project(organization=self.org).id,
+            self.create_project(organization=self.org).id,
+        ]
 
     def test_returns_no_response_if_no_homepage_query_for_user(self):
         with self.feature(FEATURES):
@@ -47,7 +51,7 @@ def test_put_updates_existing_homepage_query_to_reflect_new_data(self):
                 self.url,
                 {
                     "name": "A new homepage query update",
-                    "projects": ["-1"],
+                    "projects": self.project_ids,
                     "fields": ["field1", "field2"],
                 },
             )
@@ -57,12 +61,13 @@ def test_put_updates_existing_homepage_query_to_reflect_new_data(self):
         saved_query.refresh_from_db()
         assert saved_query.name == "A new homepage query update"
         assert saved_query.query["fields"] == ["field1", "field2"]
+        assert set(saved_query.projects.values_list("id", flat=True)) == set(self.project_ids)
 
     def test_put_creates_new_discover_saved_query_if_none_exists(self):
         homepage_query_payload = {
             "version": 2,
             "name": "New Homepage Query",
-            "projects": ["-1"],
+            "projects": self.project_ids,
             "environment": ["alpha"],
             "fields": ["environment", "platform.name"],
             "orderby": "-timestamp",
@@ -79,6 +84,7 @@ def test_put_creates_new_discover_saved_query_if_none_exists(self):
         assert new_query.name == homepage_query_payload["name"]
         assert new_query.query["fields"] == homepage_query_payload["fields"]
         assert new_query.query["environment"] == homepage_query_payload["environment"]
+        assert set(new_query.projects.values_list("id", flat=True)) == set(self.project_ids)
 
     def test_post_not_allowed(self):
         homepage_query_payload = {
```

# case141: getsentry/sentry 5cd890d8f700

File: `src/sentry/discover/endpoints/discover_saved_queries.py` · committed 2022-09-27 04:18:35-01:00 · SZZ label: RISKY

## Commit message

```
feat(discover): Add discover homepage query endpoint (#39153)

Adds `/api/0/:org-id/discover/homepage/` as a private endpoint. This
endpoint supports GET, PUT, and DELETE
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   38          ).exclude(is_homepage=True)
```

## Candidate fixes (0 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

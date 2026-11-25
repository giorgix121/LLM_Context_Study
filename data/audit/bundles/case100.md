# case100: getsentry/sentry e9ce61066783

File: `src/sentry/integrations/jira_server/client.py` · committed 2022-10-12 07:00:00-01:00 · SZZ label: RISKY

## Commit message

```
ref: type sentry/utils/assets.py and sentry/utils/http.py (#39624)
```

## Diff of the target file

```diff
@@ -126,13 +126,13 @@ class JiraServerClient(ApiClient):
         # Get a list of fields for the issue type and project
         return self.get_cached(self.ISSUE_FIELDS_URL % (project_id, issue_type_id))
 
-    def get_project_key_for_id(self, project_id):
+    def get_project_key_for_id(self, project_id) -> str:
         if not project_id:
             return ""
         projects = self.get_projects_list()
         for project in projects:
             if project["id"] == project_id:
-                return project["key"].encode("utf-8")
+                return project["key"]
         return ""
 
     def get_versions(self, project):
```

## Lines SZZ blamed (line numbers in the new version)

```
  129      def get_project_key_for_id(self, project_id) -> str:
  135                  return project["key"]
```

## Candidate fixes (0 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

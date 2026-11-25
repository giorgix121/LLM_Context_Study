# case121: getsentry/sentry 7fd8e163f316

File: `fixtures/page_objects/issue_details.py` · committed 2022-09-26 05:58:34-01:00 · SZZ label: RISKY

## Commit message

```
ref(issueDetails): Use new Tabs component (#39137)

**Before:**
<img width="828" alt="Screen Shot 2022-09-21 at 5 59 15 PM"
src="https://user-images.githubusercontent.com/44172267/191635595-4b95e0fc-c274-44c6-8c24-3a805b90670c.png">

**After:**
<img width="828" alt="Screen Shot 2022-09-21 at 6 00 28 PM"
src="https://user-images.githubusercontent.com/44172267/191635710-5d5aab13-6984-4afd-8ff4-f1b97e6bc64e.png">

Co-authored-by: Evan Purkhiser <evanpurkhiser@gmail.com>
```

## Diff of the target file

```diff
@@ -37,9 +37,9 @@ class IssueDetailsPage(BasePage):
     def api_issue_get(self, groupid):
         return self.client.get(f"/api/0/issues/{groupid}/")
 
-    def go_to_subtab(self, name):
-        tabs = self.browser.find_element(by=By.CSS_SELECTOR, value=".group-detail .nav-tabs")
-        tabs.find_element(by=By.PARTIAL_LINK_TEXT, value=name).click()
+    def go_to_subtab(self, key):
+        tabs = self.browser.find_element(by=By.CSS_SELECTOR, value='[role="tablist"]')
+        tabs.find_element(by=By.CSS_SELECTOR, value=f'[role="tab"][data-key="{key}"]').click()
         self.browser.wait_until_not('[data-test-id="loading-indicator"]')
 
     def open_issue_errors(self):
```

## Lines SZZ blamed (line numbers in the new version)

```
   40      def go_to_subtab(self, key):
   41          tabs = self.browser.find_element(by=By.CSS_SELECTOR, value='[role="tablist"]')
   42          tabs.find_element(by=By.CSS_SELECTOR, value=f'[role="tab"][data-key="{key}"]').click()
```

## Candidate fixes (0 later commits to this file remove a blamed line; 5 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

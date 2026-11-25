# case121: getsentry/sentry 7fd8e163f316

Sampled file (the only file the models saw): `fixtures/page_objects/issue_details.py` · committed 2022-09-26 05:58:34-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

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

## Other files changed by this commit (6)

- `static/app/routes.tsx` (+22 −110)
- `static/app/views/organizationGroupDetails/groupDetails.spec.jsx` (+1 −2)
- `static/app/views/organizationGroupDetails/groupDetails.tsx` (+47 −18)
- `static/app/views/organizationGroupDetails/header.tsx` (+67 −157)
- `static/app/views/organizationGroupDetails/types.tsx` (+13 −0)
- `tests/acceptance/test_issue_details.py` (+1 −1)

## Fix commits that the dataset links to this commit (3)

### Fix 1: 144bbffb8f28 (2022-09-27) · pull request #39314: fix(issueDetails): Make tab panels span full height

Pull-request labels: Scope: Frontend

Commit message:

```
fix(issueDetails): Make tab panels span full height (#39314)

**Before:**
![Screen Shot 2022-09-26 at 15 52
09](https://user-images.githubusercontent.com/44172267/192394527-f9c71cee-09de-4a9e-b194-e18b5373dfaa.png)

**After:**
![Screen Shot 2022-09-26 at 15 52
00](https://user-images.githubusercontent.com/44172267/192394525-98ac1834-3f28-44ae-bd0e-4028a65d9ea1.png)
```

Pull-request description:

```
**Before:**
![Screen Shot 2022-09-26 at 15 52 09](https://user-images.githubusercontent.com/44172267/192394527-f9c71cee-09de-4a9e-b194-e18b5373dfaa.png)

**After:**
![Screen Shot 2022-09-26 at 15 52 00](https://user-images.githubusercontent.com/44172267/192394525-98ac1834-3f28-44ae-bd0e-4028a65d9ea1.png)
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `static/app/views/organizationGroupDetails/groupDetails.tsx`: `</TabPanels>`; `</Tabs>`; `<TabPanels>`; `<Tabs`

Patch of `static/app/views/organizationGroupDetails/groupDetails.tsx` in this fix:

```diff
@@ -602,7 +602,7 @@ class GroupDetails extends Component<Props, State> {
     }
 
     return (
-      <Tabs
+      <GroupTabs
         value={currentTab}
         onChange={tab => {
           this.tabClickAnalyticsEvent(tab as Tab);
@@ -622,12 +622,12 @@ class GroupDetails extends Component<Props, State> {
           baseUrl={baseUrl}
           project={project as Project}
         />
-        <TabPanels>
+        <GroupTabPanels>
           <Item key={currentTab}>
             {isValidElement(children) ? cloneElement(children, childProps) : children}
           </Item>
-        </TabPanels>
-      </Tabs>
+        </GroupTabPanels>
+      </GroupTabs>
     );
   }
 
@@ -696,3 +696,14 @@ export default withApi(Sentry.withProfiler(GroupDetails));
 const StyledLoadingError = styled(LoadingError)`
   margin: ${space(2)};
 `;
+
+const GroupTabs = styled(Tabs)`
+  flex-grow: 1;
+`;
+
+const GroupTabPanels = styled(TabPanels)`
+  flex-grow: 1;
+  display: flex;
+  flex-direction: column;
+  justify-content: stretch;
+`;
```

### Fix 2: 4adf7d1e336d (2022-10-24) · pull request #40471: fix(issues): Remove double border in Perf Issue Details

Pull-request labels: Scope: Frontend

Commit message:

```
fix(issues): Remove double border in Perf Issue Details (#40471)

**Before:**
<img width="316" alt="Screen Shot 2022-10-24 at 2 17 22 PM"
src="https://user-images.githubusercontent.com/44172267/197631259-074f2563-00b1-42d4-b0a3-818f080dff1d.png">

**After:**
<img width="316" alt="Screen Shot 2022-10-24 at 2 17 30 PM"
src="https://user-images.githubusercontent.com/44172267/197631276-a05e70c4-dfb4-47c0-b595-4dcea6f00347.png">
```

Pull-request description:

```
**Before:**
<img width="316" alt="Screen Shot 2022-10-24 at 2 17 22 PM" src="https://user-images.githubusercontent.com/44172267/197631259-074f2563-00b1-42d4-b0a3-818f080dff1d.png">

**After:**
<img width="316" alt="Screen Shot 2022-10-24 at 2 17 30 PM" src="https://user-images.githubusercontent.com/44172267/197631276-a05e70c4-dfb4-47c0-b595-4dcea6f00347.png">
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `static/app/views/organizationGroupDetails/header.tsx`: `<StyledTabList>`

Patch of `static/app/views/organizationGroupDetails/header.tsx` in this fix:

```diff
@@ -251,7 +251,7 @@ function GroupHeader({
 
   const performanceIssueTabs = useMemo(() => {
     return (
-      <StyledTabList>
+      <StyledTabList hideBorder>
         <Item key={Tab.DETAILS} disabled={disabledTabs.includes(Tab.DETAILS)}>
           {t('Details')}
         </Item>
```

### Fix 3: a3e187e68979 (2022-09-27) · pull request #39348: fix(issueDetails): Highlight Tags tab in Tag Details page

Pull-request labels: Scope: Frontend

Commit message:

```
fix(issueDetails): Highlight Tags tab in Tag Details page (#39348)

**Before:** we're in the Tag Details page, but the "Details" tab is
highlighted
<img width="833" alt="Screen Shot 2022-09-27 at 10 49 16 AM"
src="https://user-images.githubusercontent.com/44172267/192599880-60c859f9-49d5-422e-adf6-7223ea2b2739.png">

**After:** the "Tags" tab is correctly highlighted
<img width="833" alt="Screen Shot 2022-09-27 at 10 49 01 AM"
src="https://user-images.githubusercontent.com/44172267/192599832-9e7134eb-53ed-4e6b-8342-28d62fcd6109.png">
```

Pull-request description:

```
**Before:** we're in the Tag Details page, but the "Details" tab is highlighted
<img width="833" alt="Screen Shot 2022-09-27 at 10 49 16 AM" src="https://user-images.githubusercontent.com/44172267/192599880-60c859f9-49d5-422e-adf6-7223ea2b2739.png">

**After:** the "Tags" tab is correctly highlighted
<img width="833" alt="Screen Shot 2022-09-27 at 10 49 01 AM" src="https://user-images.githubusercontent.com/44172267/192599832-9e7134eb-53ed-4e6b-8342-28d62fcd6109.png">
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `static/app/views/organizationGroupDetails/groupDetails.tsx`: `Object.values(Tab).find(tab => currentRoute.path === TabPaths[tab]) ?? Tab.DETAILS;`; `const currentTab =`

Patch of `static/app/views/organizationGroupDetails/groupDetails.tsx` in this fix:

```diff
@@ -198,8 +198,16 @@ class GroupDetails extends Component<Props, State> {
     const {event} = this.state;
 
     const currentRoute = routes[routes.length - 1];
-    const currentTab =
-      Object.values(Tab).find(tab => currentRoute.path === TabPaths[tab]) ?? Tab.DETAILS;
+
+    let currentTab: Tab;
+    // If we're in the tag details page ("/tags/:tagKey/")
+    if (router.params.tagKey) {
+      currentTab = Tab.TAGS;
+    } else {
+      currentTab =
+        Object.values(Tab).find(tab => currentRoute.path === TabPaths[tab]) ??
+        Tab.DETAILS;
+    }
 
     const baseUrl = `/organizations/${organization.slug}/issues/${group.id}/${
       router.params.eventId && event ? `events/${event.id}/` : ''
```

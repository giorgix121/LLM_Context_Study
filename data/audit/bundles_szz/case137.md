# case137: ansible/ansible d34b5786858f

Sampled file (the only file the models saw): `lib/ansible/template/native_helpers.py` · committed 2022-10-12 06:16:06-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
jinja2_native: preserve quotes in strings (#79119)

Fixes #79083
```

## Diff of the sampled file

```diff
@@ -128,7 +128,7 @@ def ansible_native_concat(nodes):
         out = ''.join([to_text(v) for v in nodes])
 
     try:
-        return ast.literal_eval(
+        evaled = ast.literal_eval(
             # In Python 3.10+ ast.literal_eval removes leading spaces/tabs
             # from the given string. For backwards compatibility we need to
             # parse the string ourselves without removing leading spaces/tabs.
@@ -136,3 +136,9 @@ def ansible_native_concat(nodes):
         )
     except (ValueError, SyntaxError, MemoryError):
         return out
+
+    if isinstance(evaled, string_types):
+        quote = out[0]
+        return f'{quote}{evaled}{quote}'
+
+    return evaled
```

## Other files changed by this commit (5)

- `changelogs/fragments/79083-jinja2_native-preserve-quotes-in-strings.yml` (+2 −0)
- `test/integration/targets/jinja2_native_types/runme.sh` (+1 −0)
- `test/integration/targets/jinja2_native_types/test_casting.yml` (+1 −1)
- `test/integration/targets/jinja2_native_types/test_concatentation.yml` (+1 −1)
- `test/integration/targets/jinja2_native_types/test_preserving_quotes.yml` (+14 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 3a6eca6670de (2022-10-13) · pull request #79131: Fix test for jinja2_native preserve quotes

Pull-request labels: bug, affects_2.15

Commit message:

```
Fix test for jinja2_native preserve quotes (#79131)

Fixes https://github.com/ansible/ansible/pull/79119#discussion_r993752129
```

Pull-request description:

```
##### SUMMARY
<!--- Describe the change below, including rationale and design decisions -->
Fixes https://github.com/ansible/ansible/pull/79119#discussion_r993752129
<!--- HINT: Include "Fixes #nnn" if you are fixing an existing issue -->

##### ISSUE TYPE
<!--- Pick one below and delete the rest -->
- Bugfix Pull Request
- Test Pull Request

##### COMPONENT NAME
<!--- Write the short name of the module, plugin, task or feature below -->

##### ADDITIONAL INFORMATION
<!--- Include additional information to help people understand the change here -->
<!--- A step-by-step reproduction of the problem is helpful if there is no related issue -->

<!--- Paste verbatim command output below, e.g. before and after your change -->
```paste below

```
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `test/integration/targets/jinja2_native_types/test_preserving_quotes.yml`: `empty_quoted_str: '""'`; `empty_str: "{{ empty_quoted_str}}"`

Patch of `test/integration/targets/jinja2_native_types/test_preserving_quotes.yml` in this fix:

```diff
@@ -10,5 +10,5 @@
         second_nested_lvl: "{{ third_nested_lvl }}"
         first_nested_lvl: "{{ second_nested_lvl }}"
         quoted_str: "{{ first_nested_lvl }}"
-        empty_quoted_str: '""'
-        empty_str: "{{ empty_quoted_str}}"
+        empty_quoted_str: "{{ empty_str }}"
+        empty_str: '""'
```

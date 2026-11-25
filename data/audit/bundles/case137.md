# case137: ansible/ansible d34b5786858f

File: `lib/ansible/template/native_helpers.py` · committed 2022-10-12 06:16:06-01:00 · SZZ label: RISKY

## Commit message

```
jinja2_native: preserve quotes in strings (#79119)

Fixes #79083
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  131          evaled = ast.literal_eval(
  139  
  140      if isinstance(evaled, string_types):
  141          quote = out[0]
  142          return f'{quote}{evaled}{quote}'
  143  
  144      return evaled
```

## Candidate fixes (0 later commits to this file remove a blamed line; 2 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

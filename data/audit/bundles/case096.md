# case096: python-poetry/poetry 1215ba8f339a

File: `src/poetry/mixology/solutions/solutions/python_requirement_solution.py` · committed 2022-10-06 02:12:59-01:00 · SZZ label: RISKY

## Commit message

```
chore: update poetry-core to 1.3 and fix deprecations
```

## Diff of the target file

```diff
@@ -12,7 +12,7 @@ if TYPE_CHECKING:
 
 class PythonRequirementSolution(Solution):  # type: ignore[misc]
     def __init__(self, exception: SolverProblemError) -> None:
-        from poetry.core.semver.helpers import parse_constraint
+        from poetry.core.constraints.version import parse_constraint
 
         from poetry.mixology.incompatibility_cause import PythonCause
```

## Lines SZZ blamed (line numbers in the new version)

```
   15          from poetry.core.constraints.version import parse_constraint
```

## Candidate fixes (0 later commits to this file remove a blamed line; 1 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

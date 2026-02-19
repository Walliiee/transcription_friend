# Research: Linting Issues in Transcription Codebase

## Research Question
Document all linting issues found in the codebase, their locations, types, and patterns.

## Summary
The transcription codebase has 35 Ruff linting errors across 11 files, with 20 errors that are auto-fixable. The project uses Ruff and Black for code quality, with configuration defined in `pyproject.toml:28-69`. The main categories of issues are:

1. **Import sorting (I001)**: 10 occurrences - unsorted or unformatted import blocks
2. **Pathlib migration (PTH)**: 9 occurrences - legacy `os.path` usage instead of modern `Path`
3. **Unused imports (F401)**: 3 occurrences - imported but never used
4. **Unused variables (RUF059)**: 4 occurrences - unpacked variables never referenced
5. **Minor issues**: Unnecessary f-strings, mode arguments, subprocess patterns

Additionally, 9 files need Black formatting, and Mypy is configured but not currently installed.

## Detailed Findings

### Linting Configuration

**File**: `pyproject.toml:28-69`

The project uses Ruff with the following configuration:
- **Target version**: Python 3.8+ (`pyproject.toml:30`)
- **Line length**: 100 characters (`pyproject.toml:33`)
- **Enabled rule categories** (`pyproject.toml:50-62`):
  - E/W: pycodestyle errors and warnings
  - F: pyflakes
  - I: isort (import sorting)
  - N: pep8-naming
  - UP: pyupgrade (modernize Python)
  - B: flake8-bugbear (likely bugs)
  - C4: flake8-comprehensions
  - SIM: flake8-simplify
  - PTH: flake8-use-pathlib
  - RUF: Ruff-specific rules

- **Ignored rules** (`pyproject.toml:65-69`):
  - E501: Line too long (Black handles this)
  - B008: Function call in argument defaults
  - PTH123: pathlib over os.path.open (gradual migration)

**Black configuration**: `pyproject.toml:83-97`
- Line length: 100 characters
- Target: Python 3.8-3.11

**Mypy configuration**: `pyproject.toml:102-119`
- Python 3.8 target
- Lenient mode: `disallow_untyped_defs = false`
- Ignores missing imports for `faster_whisper` and `ctranslate2`

### Category 1: Import Sorting Issues (I001)

Import blocks that are un-sorted or un-formatted. Auto-fixable.

**Affected files**:

1. `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:7-12`
   ```python
   import argparse
   import glob
   import os
   import sys
   from pathlib import Path
   from datetime import datetime
   ```

2. `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:17-18`
   ```python
   import torch
   import faster_whisper
   ```
   Inside function at line 17-18 (within `check_dependencies()`)

3. `scripts\extract_audio.py:26-31`
   ```python
   import argparse
   import subprocess
   import sys
   import json
   from pathlib import Path
   from typing import List, Tuple, Optional
   ```

4. `scripts\postprocess.py:12-15`
   ```python
   import argparse
   import sys
   import re
   from pathlib import Path
   ```

5. `scripts\postprocess.py:20-21`
   ```python
   from utils.corrections import get_corrections, get_review_flags
   import config
   ```

6. `scripts\transcribe.py:19-20`
   ```python
   from utils.whisper_helpers import load_model, transcribe_file, save_transcription, format_timestamp
   import config
   ```

7. `tests\test_gpu_small.py:1-2`
   ```python
   from faster_whisper import WhisperModel
   import torch
   ```

8. `utils\__init__.py:5-6`
   ```python
   from .whisper_helpers import format_timestamp, load_model, transcribe_file
   from .corrections import CORRECTIONS_EN, CORRECTIONS_DA, REVIEW_FLAGS_EN, REVIEW_FLAGS_DA
   ```

9. `utils\whisper_helpers.py:6-8`
   ```python
   from faster_whisper import WhisperModel
   from datetime import timedelta
   from pathlib import Path
   ```

**Pattern**: Standard library imports should come before third-party imports. Local imports should be last. Imports from the same module should be grouped.

### Category 2: Pathlib Migration Issues (PTH)

Legacy `os.path` usage that should be replaced with modern `Path` operations.

**Affected locations**:

1. **PTH118**: `os.path.join()` should be replaced by `Path` with `/` operator
   - `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:40`
     ```python
     search_path = os.path.join(input_dir, pattern)
     ```
   - `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:48`
     ```python
     output_file = os.path.join(output_dir, f"{base_name}.txt")
     ```

2. **PTH207**: Replace `glob.glob()` with `Path.glob()` or `Path.rglob()`
   - `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:41`
     ```python
     files = glob.glob(search_path)
     ```

3. **PTH110**: `os.path.exists()` should be replaced by `Path.exists()`
   - `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:54`
     ```python
     return os.path.exists(output_file)
     ```

4. **PTH103**: `os.makedirs()` should be replaced by `Path.mkdir(parents=True)`
   - `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:133`
     ```python
     os.makedirs(args.output_dir, exist_ok=True)
     ```

5. **PTH119**: `os.path.basename()` should be replaced by `Path.name`
   - `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:155`
     ```python
     file_name = os.path.basename(audio_file)
     ```

6. **PTH201**: Do not pass the current directory explicitly to `Path`
   - `scripts\transcribe.py:87`
     ```python
     audio_files = sorted(Path(".").glob(segment_pattern))
     ```
     Should be: `audio_files = sorted(Path().glob(segment_pattern))`

**Pattern**: The codebase is in transition from `os.path` to `pathlib.Path`. Some files use modern `Path` (like `scripts\transcribe.py`, `scripts\postprocess.py`), while others still use legacy `os.path` (primarily `batch_transcribe.py`).

### Category 3: Unused Imports (F401)

Imports that are never used in the file. Auto-fixable.

**Affected locations**:

1. `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:18`
   ```python
   import faster_whisper
   ```
   Used in `check_dependencies()` but only for existence check. Ruff suggests using `importlib.util.find_spec` instead.

2. `scripts\cleanup_originals.py:5`
   ```python
   import os
   ```
   The file uses `Path` throughout and never references `os`.

3. `scripts\transcribe.py:19`
   ```python
   from utils.whisper_helpers import load_model, transcribe_file, save_transcription, format_timestamp
   ```
   The `format_timestamp` function is imported but never called in the file.

### Category 4: Unused Variables (RUF059)

Unpacked variables that are assigned but never used. Should be prefixed with underscore.

**Affected locations**:

1. `.claude\skills\whisper-transcription\scripts\batch_transcribe.py:69`
   ```python
   segments, info = model.transcribe(audio_file, beam_size=5)
   ```
   The `info` variable is unpacked but never used.

2. `scripts\transcribe.py:275-276`
   ```python
   combined_file, segment_files = transcribe_segments(
       model,
       args.segments,
       args.language,
       args.name,
       args.interviewer,
       output_dir
   )
   ```
   Both `combined_file` and `segment_files` are unpacked but never used after.

**Pattern**: Functions return tuples, but calling code doesn't need all values. Should use underscore prefix for unused values (e.g., `_info`, `_combined_file`).

### Category 5: Subprocess Optimization (UP022)

Prefer `capture_output` over sending `stdout` and `stderr` to `PIPE`.

**Affected locations**:

1. `scripts\extract_audio.py:42-46`
   ```python
   subprocess.run(
       ["ffmpeg", "-version"],
       stdout=subprocess.PIPE,
       stderr=subprocess.PIPE,
       check=True
   )
   ```
   Should use: `capture_output=True` instead of separate `stdout` and `stderr`.

   Also occurs at:
   - `scripts\extract_audio.py:70-82` (in `is_video_file()`)
   - `scripts\extract_audio.py:122-134` (in `extract_audio()`)
   - `scripts\extract_audio.py:144-157` (fallback encoding)

### Category 6: Unnecessary F-strings (F541)

F-strings without placeholders should be regular strings.

**Affected locations**:

1. `scripts\extract_audio.py:329`
   ```python
   print(f"Batch processing complete!")
   ```
   No placeholders, should be regular string.

2. `scripts\transcribe.py:151`
   ```python
   print(f"\nAll done! Created files:")
   ```
   No placeholders, should be regular string.

### Category 7: Unnecessary Mode Argument (UP015)

Unnecessary mode argument when opening files for reading.

**Affected locations**:

1. `scripts\postprocess.py:109`
   ```python
   with open(input_file, "r", encoding="utf-8") as f:
   ```
   The `"r"` mode is default and can be omitted.

### Category 8: Unsorted __all__ List (RUF022)

The `__all__` export list should be sorted alphabetically.

**Affected locations**:

1. `utils\__init__.py:8-16`
   ```python
   __all__ = [
       'format_timestamp',
       'load_model',
       'transcribe_file',
       'CORRECTIONS_EN',
       'CORRECTIONS_DA',
       'REVIEW_FLAGS_EN',
       'REVIEW_FLAGS_DA',
   ]
   ```
   Should be sorted alphabetically (constants are mixed with functions).

## Code References by File

### High Priority Files (Multiple Issues)

**`.claude\skills\whisper-transcription\scripts\batch_transcribe.py`** - 10 issues
- Import sorting: lines 7-12, 17-18
- Unused import: line 18 (`faster_whisper`)
- Pathlib migration: lines 40, 41, 48, 54, 133, 155
- Unused variable: line 69 (`info`)

**`scripts\extract_audio.py`** - 6 issues
- Import sorting: lines 26-31
- Subprocess optimization: lines 42-46, 70-82, 122-134, 144-157
- Unnecessary f-string: line 329

**`scripts\transcribe.py`** - 5 issues
- Import sorting: lines 19-20
- Unused import: line 19 (`format_timestamp`)
- Pathlib issue: line 87 (explicit current directory)
- Unnecessary f-string: line 151
- Unused variables: lines 275-276 (`combined_file`, `segment_files`)

**`scripts\postprocess.py`** - 3 issues
- Import sorting: lines 12-15, 20-21
- Unnecessary mode: line 109

**`scripts\cleanup_originals.py`** - 1 issue
- Unused import: line 5 (`os`)

**`utils\__init__.py`** - 2 issues
- Import sorting: lines 5-6
- Unsorted `__all__`: lines 8-16

**`utils\whisper_helpers.py`** - 1 issue
- Import sorting: lines 6-8

**`tests\test_gpu_small.py`** - 1 issue
- Import sorting: lines 1-2

### Formatting Issues (Black)

Files that need Black formatting (9 files):
1. `.claude\skills\whisper-transcription\scripts\batch_transcribe.py`
2. `config.py`
3. `scripts\cleanup_originals.py`
4. `scripts\extract_audio.py`
5. `scripts\postprocess.py`
6. `scripts\transcribe.py`
7. `utils\__init__.py`
8. `utils\corrections.py`
9. `utils\whisper_helpers.py`

**Note**: 2 files already pass Black formatting.

## Existing Patterns

### Import Organization Pattern

The codebase shows two patterns:

**Pattern A** (Older files like `batch_transcribe.py`):
```python
import standard_lib1
import standard_lib2
import third_party
from pathlib import Path
from datetime import datetime
```

**Pattern B** (Newer files like `transcribe.py`, `postprocess.py`):
```python
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.whisper_helpers import ...
import config
```

**Correct isort pattern** (should be):
```python
# Standard library
import argparse
import sys
from datetime import datetime
from pathlib import Path

# Third-party
from faster_whisper import WhisperModel
import torch

# Local/first-party
from utils.whisper_helpers import ...
import config
```

### Path Handling Pattern

**Legacy pattern** (in `batch_transcribe.py`):
```python
import os
import glob

search_path = os.path.join(input_dir, pattern)
files = glob.glob(search_path)
if os.path.exists(output_file):
    ...
```

**Modern pattern** (in `transcribe.py`, `postprocess.py`, `extract_audio.py`):
```python
from pathlib import Path

audio_files = sorted(Path(".").glob(segment_pattern))
if input_file.exists():
    ...
output_dir = Path(args.output)
output_file = output_dir / f"{base_name}.txt"
```

### Error Handling Pattern

**Unused return values**:
```python
# Pattern found in multiple files
result, metadata = some_function()
# Only result is used, metadata is ignored
```

**Correct pattern**:
```python
# Use underscore for unused values
result, _metadata = some_function()
```

## Architecture Documentation

### Linting Infrastructure

**Configuration location**: `pyproject.toml:28-182`

The project has a comprehensive linting setup:

1. **Ruff** (`pyproject.toml:28-79`): Primary linter and import sorter
   - Replaces: flake8, isort, pyupgrade, multiple flake8 plugins
   - 11 rule categories enabled
   - 3 rules explicitly ignored for gradual migration

2. **Black** (`pyproject.toml:83-97`): Code formatter
   - 100 character line length
   - Standard exclusions

3. **Mypy** (`pyproject.toml:102-119`): Type checker
   - Configured but not installed (command not found in lint check)
   - Lenient mode for gradual adoption
   - Ignores missing type stubs for Whisper libraries

4. **Pytest** (`pyproject.toml:124-145`): Testing framework
   - Configured with markers for slow/integration/gpu tests

5. **Coverage** (`pyproject.toml:150-181`): Test coverage tracking
   - Currently set to 0% minimum (gradual improvement strategy)

### Linting Commands Available

**Slash commands** (from `.claude/commands/`):
- `/lint [file_or_directory]`: Run linting checks (Ruff + Black + Mypy)
- `/fix-lint [file_or_directory]`: Automatically fix linting issues

**Direct commands**:
- `ruff check .`: Check for issues
- `ruff check --fix .`: Auto-fix issues (20 of 35 are fixable)
- `ruff format .`: Format code
- `black .`: Format with Black
- `mypy .`: Type check (not currently installed)

## Open Questions

1. **Mypy installation**: Mypy is configured in `pyproject.toml:102-119` but not installed. The command fails with "command not found". Is this intentional?

2. **Gradual migration strategy**: `pyproject.toml:68` explicitly ignores `PTH123` (pathlib over os.path.open) with comment "gradual migration". Is there a plan to fully migrate all files to pathlib?

3. **batch_transcribe.py location**: This file is in `.claude\skills\whisper-transcription\scripts\` (a skill directory) rather than main `scripts\`. Is this intentional or should it be consolidated?

4. **Pre-commit hooks**: `pyproject.toml:22` lists `pre-commit>=3.0.0` as a dev dependency. Are pre-commit hooks configured and active?

5. **Function return values**: Multiple functions return tuples where not all values are used by callers. Should function signatures be reviewed, or is the pattern of ignoring values with `_` preferred?

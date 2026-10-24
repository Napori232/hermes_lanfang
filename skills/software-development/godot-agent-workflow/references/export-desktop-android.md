# Godot desktop and Android export

Use this recipe when configuring or validating Godot export targets. Keep project-specific paths, preset names, signing identities, and secrets out of this reference.

## Procedure

1. **Protect and inspect the worktree**
   - Read repository instructions, then record `git status --short` and targeted diffs.
   - Read `project.godot` and `export_presets.cfg`; reuse existing platform presets instead of rebuilding them or adding unrelated targets.
   - Put generated binaries outside the source worktree when possible.

2. **Match editor and templates exactly**
   - Run the actual editor/console binary with `--version` or derive its full stable version from the executable in use.
   - Install official templates into `%APPDATA%/Godot/export_templates/<exact-version>/`; do not reuse templates from another Godot release.
   - For a `.tpz`, validate it as a ZIP before installation. Godot template archives commonly contain a top-level `templates/` directory; copy its contents into the version directory so files such as `version.txt`, `windows_debug_x86_64.exe`, `windows_release_x86_64.exe`, `android_debug.apk`, and `android_release.apk` are directly under that directory.

3. **Check platform prerequisites without creating credentials**
   - For Windows, confirm the matching template binary exists.
   - For Android, confirm the configured SDK, build-tools, and `apksigner` exist. Use a debug export unless the user explicitly requests release signing; never invent a release keystore or expose passwords, aliases, tokens, or signing command arguments in reports.

4. **Run an editor import/parse pass**

   ```sh
   godot_console.exe --headless --path '<project>' --editor --quit
   ```

   Treat this as a prerequisite only. It can import resources and modify `.import` metadata, so compare worktree state before and after.

5. **Perform real exports for every requested target**

   ```sh
   godot_console.exe --headless --path '<project>' \
     --export-debug '<Windows preset>' '<output>/Game.exe'

   godot_console.exe --headless --path '<project>' \
     --export-debug '<Android preset>' '<output>/Game.apk'
   ```

   Preset names must match `export_presets.cfg` exactly. A successful editor load is not evidence that either export works.

6. **Validate each artifact independently**
   - Windows: require the `.exe` and companion `.pck` when the preset does not embed it; launch the exported executable with `--headless --quit-after 2` and record the exit code. Report non-fatal engine warnings separately from export failure.
   - Android: require the APK, test ZIP integrity, and run:

     ```bat
     apksigner.bat verify --verbose Game.apk
     ```

     Record the verifier exit code and accepted signature schemes, not key material.
   - Record artifact sizes and SHA-256 hashes after the final export so the report identifies the exact files tested.

7. **Audit source side effects before delivery**
   - Run `git status --short`, targeted `git diff`, and `git diff --check` after all Godot commands.
   - Separate pre-existing changes, intentional fixes, and import/test side effects. Do not commit generated binaries or silently include regenerated metadata.
   - Report exact output paths, build mode, validation results, remaining warnings, and source files changed.

## Case-only resource paths on Windows

Godot export can expose resource path case mismatches that a case-insensitive checkout hides. Compare the `res://` reference, Git's tracked spelling, the filesystem spelling, and `.import` `source_file` before editing.

If canonicalizing case is necessary, use an intermediate name so Git records the change:

```sh
git mv -f 'asset.png' 'asset.__casefix__.png'
git mv -f 'asset.__casefix__.png' 'asset.PNG'
```

Then update every reference to the same canonical spelling, run the editor import pass, and inspect any regenerated `.import` diff. Do not patch only the script path: Git, disk, import metadata, and `res://` consumers must agree or another platform can still fail.

## Gates and pitfalls

- **Use the exact matching export-template version** — editor/template drift may parse the project yet fail or produce incompatible exports.
- **Export every requested platform for real** — project loading and preset presence do not exercise pack creation, SDK tooling, alignment, or signing.
- **Verify after the final source fix** — artifacts built before a path/config correction are stale evidence.
- **Capture concise exit codes and verifier summaries directly** — wrapper output can be truncated; do not claim hashes, sizes, or validation results that were not retained.
- **Redact signing subprocess lines before surfacing logs** — exporter output may print keystore paths, aliases, and password arguments even for successful debug signing.
- **Diff after headless runs** — Godot import/editor execution can rewrite `.import` files or other metadata despite being used only as a check.

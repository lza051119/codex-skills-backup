# Codex Skills Backup

Personal Codex skills backup for moving local skills between Windows machines.

This repository intentionally includes only local skills that should be migrated:

- `codex-skills/` -> copy to `%USERPROFILE%\.codex\skills`
- `agents-skills/` -> copy to `%USERPROFILE%\.agents\skills`

It intentionally excludes:

- `%USERPROFILE%\.codex\skills\.system`
- `%USERPROFILE%\.codex\plugins\cache`

Those are Codex system skills or plugin cache entries and should normally be restored by installing Codex or enabling plugins on the new machine.

## Restore On Windows

From the repository root:

```powershell
.\restore-skills.ps1
```

Then restart Codex so it reloads the skills.

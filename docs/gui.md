# Qt GUI

Pseudonymity includes an optional native Qt GUI for users who prefer a desktop workflow alongside the CLI and Python library.

The GUI is not a different product inside the project. It is a native shell around the same engine used by the CLI and library. This matters: a dataset pseudonymised from the GUI follows the same profile rules, writes the same manifest, creates the same vault structure and produces the same risk report as a CLI run.

The goal is to make privacy-engineering workflows easier to demonstrate and review. A CLI is excellent for automation; a GUI is better when people need to see the workflow, select files, inspect outputs and discuss recovery controls together.

## Launch

```powershell
python .\pseudonymise.py gui
```

Alternative launcher:

```powershell
python .\pseudonymity_gui.py
```

## Dependencies

The GUI uses Qt through PySide6 or PyQt6. The CLI and library do not require Qt.

For package installs, use the GUI extra:

```powershell
pip install ".[gui]"
```

## Tabs

| Tab | Purpose |
| --- | --- |
| Demo | Generate sample data and run the full pseudonymisation pipeline. |
| Pseudonymise | Process an existing CSV with a selected profile. |
| Re-identify | Recover selected vault columns and optionally write an audit log. |
| Inspect CSV | Generate a JSON inspection report to help design a profile. |

## Typical Workflow

1. Open the **Inspect CSV** tab and generate an inspection report for the raw dataset.
2. Review candidate identifiers and quasi-identifiers.
3. Select a profile in the **Pseudonymise** tab.
4. Run the transformation and inspect the generated manifest and risk report.
5. If recovery is justified, use **Re-identify** with a narrow column list and an audit reason.

## Design

The GUI is intentionally thin. It does not implement separate pseudonymisation logic. It calls the same library functions used by the CLI:

- `pseudonymity.engine.pseudonymise_dataset`
- `pseudonymity.vault.reidentify_dataset`
- `pseudonymity.inspect.inspect_csv`

This keeps GUI, CLI and library behaviour aligned.

## Production Note

The GUI makes local workflows easier, but it does not replace governance controls. In production, re-identification should still require access control, approvals, audit logs and vault protection.

The GUI should therefore be understood as an operator interface, not as the policy enforcement boundary.

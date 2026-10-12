# Contributing

Improve a specific claim, model, instrument or experiment in The Bounded Observer. Start with the [branch contract](docs/branch-contract.md) and identify where the work belongs in the [project map](docs/project-structure.md).

## Contributions

- **Mathematical result:** state the model, premises, proof, countermodels and checks.
- **Application:** supply the observation and intervention interface before claiming a physical consequence.
- **Instrument:** specify behavior, comparator and verification. Scientific usefulness has a separate test.
- **Replication or experiment:** retain protocol, data, version, loss condition and result.
- **Correction:** preserve the original claim; explain the error, replacement and evidence.

The existing “new chart” issue template supports C1–C4 examples. Wider extensions use the branch contract.

## Evidence

Use [P], [D] or [H] as defined in [AGENTS.md](AGENTS.md). State numerical, implementation and empirical outcomes separately. Failed comparisons and counterexamples belong in the record.

A physical model needs units, observations, dynamics and a declared clock. A relation between branches needs a dependency or transfer claim. Cite sources you opened and retain their reuse terms.

## Check the change

```sh
pip install -e "toolkit[test]"
pytest toolkit/tests -q
python registry/validate_programme.py
```

Run checks appropriate to changed code or models. Regenerate public registry pages after changing their sources. Keep the October snapshot and frozen v2.1 unchanged; mathematical revisions become new dated releases.

## Reuse

Original code contributions use MIT; original text and figures use CC BY 4.0. Third-party material retains its licence. Supply only material you can share under the applicable terms.

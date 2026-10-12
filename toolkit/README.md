# The Bounded Observer toolkit

Version 1.1 adds selected executable operations from the current record library alongside the original v2.1 composition modules.

| Module | Scope |
| --- | --- |
| Existing composition/geometry modules | The frozen *Bounded Composition and Its Horizons* v2.1 results; their existing interfaces remain |
| [bounded.records](RECORDS.md) | Supplied retained-algebra expectation and forgetting, locally covariant CP-rate cone, and log full-rank exposure bounds |
| [bounded.hormesis](HORMESIS.md) | Three distinct response models with exact conditional peak/assay laws and a finite series-flux model |

The live modules implement their stated mathematical models. They require a specified algebra, rates, dynamics or response parameters; they do not select an actual physical or biological model. General noncommuting-mean Gibbs optimization and radiation readers remain future tasks, not implemented APIs in this release.

## Install and check

```sh
python -m pip install -e "toolkit[test]"
python -m pytest toolkit/tests -q
```

## Try a current record operation

```python
import numpy as np
from bounded.records import RetainedAlgebra, normalize_record

rho = normalize_record(np.diag([4., 1., 2., 3.]))
algebra = RetainedAlgebra([(2, 2)])
selected = algebra.expectation(rho)
after = algebra.forget(rho, exposure=0.7)
assert np.allclose(algebra.expectation(after), selected)
```

## Try a model-specific response

```python
from bounded.hormesis import AdditiveHill

model = AdditiveHill(p0=0.5, repair=0.6, harm=1.5,
                     activation=1.0, toxicity=10.0, exponent=2.0)
print(model.peak())
print(model.detectable_interval(gain=0.05))
```

Read the module documents for premises, numerical tolerances and boundary cases. Normalization validates the cone in trace-one units so tiny raw magnitudes cannot hide a materially invalid normalized record.

The [publication snapshot](../papers/library-2026-10-12/) remains frozen. The toolkit is the evolving implementation: changes need source attribution, meaningful independent checks and a versioned receipt.

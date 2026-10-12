# Finite complex records

`bounded.records` implements three current, source-scoped models from the
[2026 library](../papers/library-2026-10-12/README.md):

| Operation | Required input and premises | Source |
| --- | --- | --- |
| Retained-algebra forgetting | A specified finite complex matrix algebra; trace-preserving conditional expectation and complete positivity | [Paper 4, Theorem 5](../papers/library-2026-10-12/papers/paper4.md) |
| Local-covariant relaxation | A time-homogeneous trace-preserving quantum Markov generator covariant under all local unitaries, with factor dimensions at least two | [Paper 8, Theorem 5](../papers/library-2026-10-12/papers/paper8.md) |
| Full-rank exposure bound | A well-defined finite-dimensional time-local GKSL evolution, a full-rank initial state, and finite integrated activity for a specified jump representation | [Paper 4, Theorem 6](../papers/library-2026-10-12/papers/paper4.md) |

These are executable mathematical models. Identifying a matrix with a physical,
biological or competition record requires a separate declared model and test.
The functions do not select the retained algebra, kinetic coefficients or clock.

`normalize_record` checks Hermiticity and positivity in normalized trace-one
units before removing negligible roundoff. Its tolerance therefore cannot admit
a materially invalid ray merely because the raw matrix is tiny. An internal
positive rescaling also handles finite records whose raw trace would overflow.
The standalone `validate_record` instead uses an absolute tolerance on its
supplied matrix and does not normalize it. Neither function clips eigenvalues.

## Preserve a complete algebra of readings

```python
import numpy as np
from bounded.records import RetainedAlgebra, normalize_record

rho = normalize_record(np.diag([4., 1., 2., 3.]))
algebra = RetainedAlgebra([(2, 2)])
selected = algebra.expectation(rho)
after = algebra.forget(rho, exposure=0.7)
assert np.allclose(algebra.expectation(after), selected)
```

`[(n, k)]` means the retained algebra is `M_n(C) ⊗ I_k`: the complete readings
on the first factor are retained; its multiplicity factor is forgotten. Several
pairs specify the direct sum of these blocks. For example, `[(1, 1)] * d`
retains all diagonal readings of a `d`-dimensional record. An optional `unitary`
specifies the basis of the supplied algebra.

The expectation removes cross-block coherences and sends each block to
`Tr_k(X) ⊗ I_k/k`. It acts on any complex operator so its complete positivity can
be checked by applying it to matrix units. `forget` instead requires a normalized
positive record. Its exposure is nonnegative and additive:
`T_u(T_v(rho)) = T_(u+v)(rho)`. The limit is the unique maximum-entropy state
with **all** retained-algebra readings. A few arbitrary mean constraints need
not have a universal linear maximum-entropy selector; this module supplies none.

## Check the admissible relaxation cone

```python
from bounded.records import (
    local_covariant_sector_rates,
    local_covariant_coefficients,
    is_local_covariant_rate_triple,
    local_covariant_channel,
)

rates = local_covariant_sector_rates(2, 3, (0.4, 0.2, 0.7))
assert is_local_covariant_rate_triple(2, 3, rates)
coefficients = local_covariant_coefficients(2, 3, rates)
rho6 = np.eye(6) / 6
after = local_covariant_channel(rho6, 2, 3, rates, exposure=0.5)
assert not is_local_covariant_rate_triple(2, 3, (1., 1., 3.))
```

The three decay rates act on the traceless first-factor, second-factor and
correlation sectors. Positive rates alone do not guarantee complete positivity.
The coefficients `(x, y, z)` must be nonnegative. The identity sector stays fixed;
the generator itself is not asserted to be a positive map.

The cone check is strict by default. Floating-point reconstruction on a cone
face may produce a small negative residue. A caller can explicitly supply an
appropriate `atol` to the inverse conversion, membership check and channel.
Only accepted residues are replaced by zero; the channel recomputes its rates
from those nonnegative coefficients. This tolerance is numerical, not a new
admissible physical rate or a fitted projection.

## Use activity rather than assume a clock

```python
from bounded.records import gksl_exposure_rate, log_full_rank_lower_bound

initial = np.diag([0.7, 0.3])
jump = np.array([[0., np.sqrt(0.8)], [0., 0.]])
rate = gksl_exposure_rate([jump])
log_lower_bound = log_full_rank_lower_bound(initial, exposure=rate * 2.)
```

For constant jumps the integrated activity is time multiplied by the returned
rate. For time-dependent jumps the caller must integrate
`||sum_k L_k(t).conj().T @ L_k(t)||_op` in the supplied clock. Under a smooth
increasing clock change, the jumps rescale by the square root of its Jacobian;
the integral is unchanged. Scalar shifts of the jump representation can change
this integral, so that representation must be specified or canonically fixed.

`log_full_rank_lower_bound` returns `log(p0) - Xi`. The logarithmic form remains
finite when exponentiating it would underflow in ordinary floating-point
arithmetic. `qubit_rapidity_upper_bound` evaluates the associated binary radial
bound. Neither function establishes a finite bound for arbitrary proposed
dynamics: finite parameter time need not mean finite activity. A bounded
system-bath swap can purify in finite time while its local GKSL activity diverges.

## Reproduce the checks

Install the toolkit with its test dependencies, then run from the repository root:

```text
python -m pytest toolkit/tests/test_records.py -q
```

The checks include independent finite twirls; Choi positivity and trace
preservation; preservation of every retained block matrix-unit reading;
idempotence, semigroup composition and the entropy identity including a singular
support case; direct GKSL exponentiation of all matrix units in several factor
dimensions; invalid-rate Choi negativity; noncommuting GKSL evolution and sharp
amplitude-damping bounds; clock changes; and a finite-swap scope counterexample.
They certify the stated finite models, rather than observations of nature.

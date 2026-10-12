"""Independent finite checks: equilibrium selection versus dynamical selection."""
import json
import numpy as np

def vec(a):
    return np.asarray(a, complex).reshape(-1, order="F")

def unvec(a, d):
    return np.asarray(a, complex).reshape((d, d), order="F")

def superoperator(action, d):
    columns = []
    for j in range(d):
        for i in range(d):
            e = np.zeros((d, d), complex)
            e[i, j] = 1
            columns.append(vec(action(e)))
    return np.column_stack(columns)

def exponential(generator, t):
    assert np.allclose(generator, generator.conj().T)
    w, v = np.linalg.eigh(generator)
    return (v * np.exp(t * w)) @ v.conj().T

def common_checks(generator, d):
    identity = np.eye(d, dtype=complex)
    stationary = identity / d
    assert np.linalg.norm(generator @ vec(stationary)) < 1e-12
    assert np.linalg.norm(generator.conj().T @ vec(identity)) < 1e-12
    assert np.linalg.matrix_rank(generator.conj().T, tol=1e-10) == d*d - 1
    channel = exponential(generator, 0.73)
    choi = np.zeros((d*d, d*d), complex)
    for i in range(d):
        for j in range(d):
            e = np.zeros((d, d), complex)
            e[i, j] = 1
            choi += np.kron(e, unvec(channel @ vec(e), d))
    assert np.linalg.eigvalsh(choi).min() > -1e-10
    assert np.allclose(vec(identity).conj() @ channel, vec(identity).conj())
    assert np.allclose(channel @ vec(stationary), vec(stationary))
    depolarization = np.outer(vec(stationary), vec(identity).conj())
    assert np.linalg.norm(exponential(generator, 100) - depolarization) < 1e-9
    return [-float(x) for x in np.linalg.eigvalsh(generator) if x < -1e-10]

def product_models():
    da, db, d = 2, 3, 6
    ia, ib = np.eye(da), np.eye(db)
    def reset_a(rho):
        return np.kron(ia/da, np.trace(rho.reshape(da,db,da,db), axis1=0, axis2=2))
    def reset_b(rho):
        return np.kron(np.trace(rho.reshape(da,db,da,db), axis1=1, axis2=3), ib/db)
    rng = np.random.default_rng(260012)
    ua, _ = np.linalg.qr(rng.normal(size=(da,da)) + 1j*rng.normal(size=(da,da)))
    ub, _ = np.linalg.qr(rng.normal(size=(db,db)) + 1j*rng.normal(size=(db,db)))
    unitary = np.kron(ua, ub)
    raw = rng.normal(size=(d,d)) + 1j*rng.normal(size=(d,d))
    rho = raw @ raw.conj().T
    rho /= np.trace(rho)
    polarization_a = np.kron(np.diag([1,-1]), ib)
    polarization_b = np.kron(ia, np.diag([1,-1,0]))
    reports = []
    for ga, gb in [(0.5,0.5), (0.25,0.75)]:
        def action(state):
            return ga*(reset_a(state)-state) + gb*(reset_b(state)-state)
        generator = superoperator(action, d)
        rates = common_checks(generator, d)
        assert np.allclose(action(unitary @ rho @ unitary.conj().T),
                           unitary @ action(rho) @ unitary.conj().T)
        assert np.allclose(action(polarization_a), -ga*polarization_a)
        assert np.allclose(action(polarization_b), -gb*polarization_b)
        values, counts = np.unique(np.round(rates,9), return_counts=True)
        actual = dict(zip(values.tolist(), counts.tolist()))
        expected = {}
        for rate, mult in [(ga,3), (gb,8), (ga+gb,24)]:
            expected[rate] = expected.get(rate,0) + mult
        assert actual == expected
        reports.append({
            "gamma_a":ga, "gamma_b":gb, "common_total_rate":ga+gb,
            "physical_ratio":ga/gb, "stationary_state":"I6/6",
            "conserved_algebra":"C I6", "entropy_nats":float(np.log(d)),
            "nonzero_decay_spectrum":actual,
            "product_unitary_covariance":True, "channel_cp_checked":True
        })
    assert reports[0]["physical_ratio"] != reports[1]["physical_ratio"]
    return reports

def pauli_models():
    paulis = [np.array([[0,1],[1,0]],complex),
              np.array([[0,-1j],[1j,0]],complex),
              np.diag([1,-1]).astype(complex)]
    reports = []
    for gammas in [(1/6,1/6,1/6), (1/12,1/6,1/4)]:
        generator = superoperator(
            lambda rho: sum(g*(p@rho@p-rho) for g,p in zip(gammas,paulis)),2)
        common_checks(generator,2)
        decay = [2*(sum(gammas)-g) for g in gammas]
        for p,rate in zip(paulis,decay):
            assert np.allclose(generator@vec(p), -rate*vec(p))
        reports.append({
            "gamma":list(gammas), "common_total_rate":sum(gammas),
            "polarization_decay_rates":decay,
            "dimensionless_max_min_ratio":max(decay)/min(decay),
            "stationary_state":"I2/2", "conserved_algebra":"C I2",
            "entropy_nats":float(np.log(2)), "channel_cp_checked":True
        })
    assert reports[0]["dimensionless_max_min_ratio"] != reports[1]["dimensionless_max_min_ratio"]
    return reports

if __name__ == "__main__":
    print(json.dumps({
        "status":"all checks passed",
        "covariant_product_models":product_models(),
        "pauli_models":pauli_models(),
        "conclusion":"Same entropy-maximizing stationary state and conserved algebra, different calibrated dynamical ratios."
    },indent=2))

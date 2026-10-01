import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createValley, stepValley, observeValley, revealValley, VALLEY_RULES } from './valley-world.mjs';

const doAction = (world, action) => stepValley(world, action);
const choose = (world, choice) => doAction(world, { type: 'decide', choice });

test('[P, conditional model] opposite hidden causes have the same initial local appearance', () => {
  for (const home of ['estuary', 'ridge']) {
    const pressure = observeValley(createValley(home, 1));
    const retention = observeValley(createValley(home, 2));
    assert.deepEqual(pressure, retention);
    assert.equal(pressure.scene.gateClosed, true);
    assert.equal(pressure.scene.riverLevel, home === 'estuary' ? 'low' : 'pooled');
    assert.equal(pressure.scene.localLandmarks.some((item) => item.id === 'gate'), true);
    assert.equal(Object.hasOwn(pressure, 'cause'), false);
    assert.equal(JSON.stringify(pressure).includes('"cause"'), false);
    assert.notEqual(pressure.memory, observeValley(createValley(home === 'estuary' ? 'ridge' : 'estuary', 1)).memory);
  }
});

test('[P, conditional model] only an actual Ridge gauge inspection distinguishes causes', () => {
  const estuaryPressure = doAction(createValley('estuary', 1), { type: 'inspect' });
  const estuaryRetention = doAction(createValley('estuary', 2), { type: 'inspect' });
  assert.deepEqual(observeValley(estuaryPressure), observeValley(estuaryRetention));
  assert.equal(observeValley(estuaryPressure).inspections[0].pressure, undefined);

  const atRidgePressure = doAction(createValley('estuary', 1), { type: 'travel' });
  const atRidgeRetention = doAction(createValley('estuary', 2), { type: 'travel' });
  assert.deepEqual(observeValley(atRidgePressure), observeValley(atRidgeRetention));
  const pressure = observeValley(doAction(atRidgePressure, { type: 'inspect' }));
  const retention = observeValley(doAction(atRidgeRetention, { type: 'inspect' }));
  assert.equal(pressure.inspections[0].pressure, 'high');
  assert.equal(retention.inspections[0].pressure, 'low');
  assert.equal(pressure.scene.inspection.pressure, 'high');
  assert.match(pressure.inference, /I measured high/);
  assert.match(retention.inference, /I measured low/);
  assert.doesNotMatch(pressure.inference, /\[P\]|constructed world/);
});

test('[P, conditional model] the same opening can help one hidden world and flood the other', () => {
  const openedPressure = choose(createValley('estuary', 1), 'open');
  const openedRetention = choose(createValley('estuary', 2), 'open');
  assert.equal(revealValley(openedPressure).cause, 'pressure');
  assert.equal(revealValley(openedRetention).cause, 'retention');
  assert.equal(revealValley(openedPressure).chosen.effects.estuaryHomesFlooded, 5);
  assert.equal(revealValley(openedRetention).chosen.effects.estuaryHomesFlooded, 0);
  assert.equal(revealValley(openedRetention).chosen.effects.ridgeFieldsDry, 2);
  assert.equal(revealValley(choose(createValley('estuary', 1), 'hold')).chosen.effects.estuaryFieldsDry, 1);
  assert.equal(revealValley(choose(createValley('estuary', 2), 'hold')).chosen.effects.estuaryFieldsDry, 4);
  assert.equal(observeValley(openedPressure).scene.riverLevel, 'surge');
  assert.equal(observeValley(openedRetention).scene.riverLevel, 'flowing');
});

test('[P, conditional model] travel and inquiry cost days; delay dries downstream fields', () => {
  let world = createValley('estuary', 2);
  const immediate = revealValley(choose(world, 'open')).chosen;
  world = doAction(world, { type: 'travel' });
  assert.equal(world.day, 1);
  assert.equal(world.location, 'ridge');
  world = doAction(world, { type: 'inspect' });
  assert.equal(world.day, 2);
  world = doAction(world, { type: 'listen' });
  assert.equal(world.day, 3);
  assert.equal(observeValley(world).available.travel, false);
  assert.equal(doAction(world, { type: 'travel' }), world);
  const delayed = revealValley(choose(world, 'open')).chosen;
  assert.equal(delayed.late, true);
  assert.equal(delayed.effects.estuaryFieldsDry, immediate.effects.estuaryFieldsDry + 2);
  assert.equal(delayed.responseDay, 3);
  const ridgeReading = observeValley(choose(world, 'open'));
  assert.doesNotMatch(ridgeReading.outcome.copy, /two additional downstream fields dried/);
  assert.match(ridgeReading.outcome.copy, /not visible from here/);
});

test('[P, conditional model] later home memories differ and daily practice responds to local harm', () => {
  const estuaryFirst = choose(createValley('estuary', 1), 'open');
  const ridgeFirst = choose(createValley('ridge', 1), 'open');
  const estuaryNext = observeValley(doAction(estuaryFirst, { type: 'next' }));
  const ridgeNext = observeValley(doAction(ridgeFirst, { type: 'next' }));
  assert.equal(estuaryNext.era, 1);
  assert.equal(ridgeNext.era, 1);
  assert.notEqual(estuaryNext.memory, ridgeNext.memory);
  assert.match(estuaryNext.memory, /5 homes flooded here/);
  assert.doesNotMatch(ridgeNext.memory, /homes flooded/);
  assert.match(estuaryNext.identity.work, /replace washed planks/);
  assert.match(ridgeNext.identity.work, /check pool marks/);
  assert.equal(estuaryNext.priorOutcomes.length, 1);
  assert.equal(estuaryNext.lineage.length, 2);
  assert.equal(estuaryNext.record, null, 'the current generation has not yet written its record');
  assert.equal(observeValley(estuaryFirst).memory, observeValley(createValley('estuary', 1)).memory,
    'inherited memory stays fixed during the generation that acts');
});

test('[P, conditional model] three generations are reachable with alternating hidden causes', () => {
  let world = createValley('estuary', 1);
  const causes = [];
  const years = [];
  for (let era = 0; era < VALLEY_RULES.generations; era++) {
    years.push(observeValley(world).year);
    world = choose(world, 'hold');
    causes.push(revealValley(world).cause);
    if (era < VALLEY_RULES.generations - 1) {
      assert.equal(observeValley(world).available.next, true);
      world = doAction(world, { type: 'next' });
    }
  }
  assert.deepEqual(years, [0, 35, 70]);
  assert.deepEqual(causes, ['pressure', 'retention', 'pressure']);
  assert.equal(observeValley(world).available.next, false);
  assert.equal(doAction(world, { type: 'next' }), world);
  assert.equal(observeValley(world).lineage.length, 3,
    'the current generation is not inherited until a descendant arrives');
});

test('[P, conditional model] coordination needs contact and evidence or trust, and costs time and supplies', () => {
  const unprepared = choose(createValley('estuary', 1), 'coordinate');
  assert.equal(revealValley(unprepared).chosen.coordinated, false);
  assert.equal(observeValley(unprepared).scene.gateClosed, true);
  assert.equal(revealValley(unprepared).chosen.effects.jointSuppliesSpent, 1);

  let prepared = createValley('estuary', 1);
  prepared = doAction(prepared, { type: 'travel' });
  prepared = doAction(prepared, { type: 'inspect' });
  assert.equal(observeValley(prepared).available.coordinationReady, true);
  prepared = choose(prepared, 'coordinate');
  const first = revealValley(prepared).chosen;
  assert.equal(first.coordinated, true);
  assert.equal(first.responseDay, 3);
  assert.equal(first.late, true);
  assert.equal(first.effects.jointSuppliesSpent, 1);
  assert.equal(first.effects.estuaryHomesFlooded, 0);
  assert.equal(first.effects.estuaryFieldsDry, 2, 'delay still harms downstream fields');

  let descendant = doAction(prepared, { type: 'next' });
  descendant = doAction(descendant, { type: 'travel' });
  assert.equal(observeValley(descendant).available.coordinationReady, true,
    'a documented shared plan contributes inherited trust');
  descendant = choose(descendant, 'coordinate');
  const second = revealValley(descendant).chosen;
  assert.equal(second.coordinated, true);
  assert.equal(second.responseDay, 2);
  assert.equal(second.late, false);
  assert.equal(second.effects.jointSuppliesSpent, 1);
  const missedWindow = choose(doAction(doAction(doAction(createValley('estuary', 1), { type: 'listen' }),
    { type: 'travel' }), { type: 'listen' }), 'coordinate');
  assert.equal(revealValley(missedWindow).chosen.responseDay, 4);
  assert.match(observeValley(missedWindow).dayLabel, /response reached day 4/);
});

test('[P, conditional model] reveal is gated and exposes both records and choice comparisons only after decision', () => {
  const world = createValley('estuary', 1);
  assert.throws(() => revealValley(world), /committed decision/);
  const result = choose(world, 'hold');
  const publicReading = observeValley(result);
  assert.equal(Object.hasOwn(publicReading, 'cause'), false);
  assert.equal(publicReading.knownEffects.homesFlooded, 0);
  assert.equal(Object.hasOwn(publicReading.knownEffects, 'ridgeFieldsDry'), false);
  const truth = revealValley(result);
  assert.notEqual(truth.inheritedRecords.estuary.text, truth.inheritedRecords.ridge.text);
  assert.equal(truth.inheritedRecords.estuary.year, -35);
  assert.equal(truth.records.estuary.length, 1);
  assert.equal(truth.records.ridge.length, 1);
  assert.ok(truth.counterfactuals.sameCause.open.effects.estuaryHomesFlooded > 0);
  assert.equal(truth.counterfactuals.oppositeCause.cause, 'retention');
  assert.equal(truth.counterfactuals.oppositeCause.choices.open.effects.estuaryHomesFlooded, 0);
  assert.ok(truth.assumptions.every((line) => line.startsWith('Model rule:')));
});

test('[P, conditional model] a traveler at Ridge cannot read their newly written Estuary record before reveal or descent', () => {
  let world = createValley('estuary', 2); // water retention
  world = doAction(world, { type: 'travel' });
  world = doAction(world, { type: 'inspect' });
  world = choose(world, 'hold');
  const ridgeReading = observeValley(world);
  assert.equal(ridgeReading.location, 'ridge');
  assert.equal(ridgeReading.record, null);
  assert.equal(ridgeReading.lineage.length, 1);
  assert.equal(ridgeReading.lineage[0].year, -35);
  assert.equal(ridgeReading.outcome.copy.includes('4 fields dried'), false);
  assert.equal(JSON.stringify(ridgeReading).includes('4 fields dried'), false);
  assert.equal(revealValley(world).records.estuary.at(-1).impact.fieldsDry, 4,
    'the comparison panel may disclose the other community after commitment');
  const descendant = observeValley(doAction(world, { type: 'next' }));
  assert.match(descendant.memory, /4 fields dried/);
  assert.equal(descendant.lineage.length, 2);
});

/* A constructed social world, with declared rules rather than claims about
   real histories or consciousness. Private causes and community records stay
   outside the observer's reading until an action makes them accessible. */

const COMMUNITIES = ['estuary', 'ridge'];
const CAUSES = ['pressure', 'retention'];
const INITIAL_MEMORY = Object.freeze({
  estuary: 'A generation ago the closed gate left our channel thin. We rationed for days. We never saw the gate gauge.',
  ridge: 'A generation ago a closed gate held a dangerous crest. The gate needed repairs. We did not see the downstream rationing.',
});

export const VALLEY_RULES = Object.freeze({
  generations: 3,
  yearsBetweenGenerations: 35,
  lastInquiryDay: 3,
  lateResponseAt: 3,
  inquiryDayCost: 1,
  coordinationDayCost: 1,
  coordinationSupplyCost: 1,
  assumptions: Object.freeze([
    'Model rule: the gate begins closed and downstream flow looks low in every generation.',
    'Model rule: a high gate stress reading means a full immediate opening sends a damaging surge; a low reading means held irrigation water can be released without that surge.',
    'Model rule: travel, inspection, and listening each use one day. Joint planning uses one additional day and one supply unit. A response on day 3 or later dries additional downstream fields.',
    'Model rule: a shared staged release forms only after cross-community contact plus a Ridge gauge reading or inherited trust. An unprepared attempt spends its supply but leaves the gate closed.',
  ]),
});

const copyRecord = (item) => ({ ...item, impact: { ...item.impact } });
const copyRecords = (records) => ({
  estuary: records.estuary.map(copyRecord),
  ridge: records.ridge.map(copyRecord),
});
const otherCommunity = (place) => place === 'estuary' ? 'ridge' : 'estuary';
const otherCause = (cause) => cause === 'pressure' ? 'retention' : 'pressure';
const event = (world, text) => [...world.journal, { day: world.day, text }];

function causeFor(seed, era) {
  const first = (seed & 1) === 1 ? 'pressure' : 'retention';
  return era % 2 === 0 ? first : otherCause(first);
}

function trust(world) {
  const distinctTestimonies = new Set(world.testimonies.map((entry) => entry.location)).size;
  return Math.min(2, world.cooperativePast * 2 + distinctTestimonies);
}

function hasRidgeGauge(world) {
  return world.inspections.some((entry) => entry.location === 'ridge');
}

function canCoordinate(world) {
  return world.contacted && (hasRidgeGauge(world) || trust(world) >= 2);
}

function resolvedEffects(cause, choice, context) {
  const responseDay = context.day + (choice === 'coordinate' ? VALLEY_RULES.coordinationDayCost : 0);
  const late = responseDay >= VALLEY_RULES.lateResponseAt;
  const coordinated = choice === 'coordinate' && context.coordinationReady;
  const actionTaken = choice === 'coordinate' && !coordinated ? 'hold' : choice;
  const effects = {
    estuaryHomesFlooded: 0,
    estuaryFieldsDry: 0,
    ridgeFieldsDry: 0,
    gateRepairsNeeded: 0,
    jointSuppliesSpent: choice === 'coordinate' ? VALLEY_RULES.coordinationSupplyCost : 0,
  };

  if (cause === 'pressure') {
    if (actionTaken === 'open') effects.estuaryHomesFlooded = 5;
    if (actionTaken === 'hold') {
      effects.estuaryFieldsDry = 1;
      effects.gateRepairsNeeded = 1;
    }
    if (actionTaken === 'coordinate') effects.gateRepairsNeeded = 1;
  } else {
    if (actionTaken === 'open') effects.ridgeFieldsDry = 2;
    if (actionTaken === 'hold') effects.estuaryFieldsDry = 4;
    if (actionTaken === 'coordinate') {
      effects.estuaryFieldsDry = 1;
      effects.ridgeFieldsDry = 1;
    }
  }
  if (late) effects.estuaryFieldsDry += 2;

  return {
    choice,
    responseDay,
    late,
    coordinated,
    effects,
  };
}

function recordsFor(world, outcome) {
  const { effects } = outcome;
  const gateWord = outcome.choice === 'open' || outcome.coordinated ? 'opened' : 'stayed closed';
  const estuaryParts = [
    `Year ${world.era * 35}: The gate ${gateWord}.`,
    `${effects.estuaryHomesFlooded} homes flooded here; ${effects.estuaryFieldsDry} fields dried.`,
  ];
  const ridgeParts = [
    `Year ${world.era * 35}: The gate ${gateWord}.`,
    `${effects.ridgeFieldsDry} ridge fields dried; ${effects.gateRepairsNeeded} gate repairs were needed.`,
  ];
  if (outcome.choice === 'coordinate') {
    const plan = outcome.coordinated
      ? 'Both communities made a shared release plan.'
      : 'A shared release plan failed to form.';
    estuaryParts.push(plan);
    ridgeParts.push(plan);
    if (outcome.coordinated || world.home === 'estuary') estuaryParts.push('One supply unit went to the plan.');
    if (outcome.coordinated || world.home === 'ridge') ridgeParts.push('One supply unit went to the plan.');
  }
  if (outcome.late) {
    estuaryParts.push('The response came late while the channel stayed low.');
    ridgeParts.push('The response came after the usual decision window.');
  }
  if (hasRidgeGauge(world)) {
    const reading = world.cause === 'pressure' ? 'high' : 'low';
    ridgeParts.push(`A gate stress gauge read ${reading}.`);
    if (outcome.coordinated || world.home === 'estuary') {
      estuaryParts.push(`A carried gate stress reading was ${reading}.`);
    } else {
      estuaryParts.push('No gate stress reading reached this record.');
    }
  } else {
    ridgeParts.push('No gate stress reading entered this record.');
    estuaryParts.push('No gate stress reading reached this record.');
  }
  if (world.home === 'estuary' && world.testimonies.some((entry) => entry.location === 'ridge')) {
    estuaryParts.push('A Ridge resident described the old dangerous crest, without claiming to know today’s pressure.');
  }
  if (world.home === 'ridge' && world.testimonies.some((entry) => entry.location === 'estuary')) {
    ridgeParts.push('An Estuary resident described the old downstream rationing.');
  }
  return {
    estuary: {
      era: world.era, year: world.era * 35, text: estuaryParts.join(' '),
      impact: { homesFlooded: effects.estuaryHomesFlooded, fieldsDry: effects.estuaryFieldsDry },
      sharedPlan: outcome.coordinated,
    },
    ridge: {
      era: world.era, year: world.era * 35, text: ridgeParts.join(' '),
      impact: { fieldsDry: effects.ridgeFieldsDry, gateRepairsNeeded: effects.gateRepairsNeeded },
      sharedPlan: outcome.coordinated,
    },
  };
}

/** Model construction: the seed changes hidden causes, but not the public opening
    scene. Descendants begin at their home and inherit only its written record. */
export function createValley(home = 'estuary', seed = 1) {
  if (!COMMUNITIES.includes(home)) throw new RangeError('home must be estuary or ridge');
  if (!Number.isSafeInteger(seed)) throw new RangeError('seed must be a safe integer');
  return {
    home,
    seed,
    era: 0,
    day: 0,
    phase: 'inquiry',
    location: home,
    cause: causeFor(seed, 0),
    testimonies: [],
    inspections: [],
    contacted: false,
    cooperativePast: 0,
    inheritedMemory: INITIAL_MEMORY[home],
    records: { estuary: [], ridge: [] },
    choice: null,
    outcome: null,
    journal: [{ day: 0, text: 'A closed gate stands between the two communities. The downstream channel is low.' }],
    eventCue: null,
  };
}

/** Model rule: each inquiry spends a day. Decisions are irreversible for
    the current generation. Returning the same object means an action was not
    available; no hidden cause is silently advanced by such an attempt. */
export function stepValley(world, action) {
  if (!world || !action || typeof action.type !== 'string') {
    throw new TypeError('stepValley needs a world and an action with a type');
  }

  if (action.type === 'next') {
    if (world.phase !== 'result' || world.era >= VALLEY_RULES.generations - 1) return world;
    const era = world.era + 1;
    return {
      ...world,
      era,
      day: 0,
      phase: 'inquiry',
      location: world.home,
      cause: causeFor(world.seed, era),
      testimonies: [],
      inspections: [],
      contacted: false,
      cooperativePast: world.cooperativePast + Number(world.outcome.coordinated),
      inheritedMemory: world.records[world.home].at(-1).text,
      choice: null,
      outcome: null,
      journal: [{ day: 0, text: `Year ${era * 35}: A descendant comes to the closed gate with a local inherited account.` }],
      eventCue: `Year ${era * 35}. Your home kept its own record of the last closure.`,
    };
  }

  if (world.phase !== 'inquiry') return world;

  if (action.type === 'travel') {
    if (world.day >= VALLEY_RULES.lastInquiryDay) return world;
    const location = otherCommunity(world.location);
    const next = {
      ...world,
      day: world.day + 1,
      location,
      contacted: world.contacted || location !== world.home,
      eventCue: `You reached ${location === 'ridge' ? 'Ridge' : 'Estuary'}. One day passed.`,
    };
    next.journal = event(next, next.eventCue);
    return next;
  }

  if (action.type === 'inspect') {
    if (world.day >= VALLEY_RULES.lastInquiryDay || world.inspections.some((entry) => entry.location === world.location)) return world;
    const finding = world.location === 'ridge'
      ? `Gate stress gauge reads ${world.cause === 'pressure' ? 'high' : 'low'} pressure.`
      : 'Downstream flow measures low; this reading alone does not identify why the gate is shut.';
    const inspection = {
      location: world.location,
      day: world.day + 1,
      finding,
      ...(world.location === 'ridge' ? { pressure: world.cause === 'pressure' ? 'high' : 'low' } : {}),
    };
    const next = {
      ...world,
      day: world.day + 1,
      inspections: [...world.inspections, inspection],
      eventCue: finding,
    };
    next.journal = event(next, `Inspection at ${world.location}: ${finding}`);
    return next;
  }

  if (action.type === 'listen') {
    if (world.day >= VALLEY_RULES.lastInquiryDay || world.testimonies.some((entry) => entry.location === world.location)) return world;
    const text = world.location === 'estuary'
      ? 'Our channel is thin again. Our elders remember rationing, but no one here saw the gate gauge then or now.'
      : 'The gate is shut again. Our elders remember a dangerous crest, but the path view cannot tell us whether today is the same.';
    const testimony = { location: world.location, day: world.day + 1, text };
    const next = {
      ...world,
      day: world.day + 1,
      testimonies: [...world.testimonies, testimony],
      eventCue: `A person at ${world.location} told you what they remember and see.`,
    };
    next.journal = event(next, `Testimony at ${world.location}: ${text}`);
    return next;
  }

  if (action.type === 'decide') {
    if (!['open', 'hold', 'coordinate'].includes(action.choice)) {
      throw new RangeError('choice must be open, hold, or coordinate');
    }
    const outcome = resolvedEffects(world.cause, action.choice, {
      day: world.day,
      coordinationReady: canCoordinate(world),
    });
    const newRecords = recordsFor(world, outcome);
    const records = copyRecords(world.records);
    for (const community of COMMUNITIES) records[community].push(newRecords[community]);
    const eventCue = action.choice === 'coordinate'
      ? (outcome.coordinated ? 'A shared plan formed. It took a day and supplies.' : 'The shared plan failed to form; the gate stayed closed.')
      : (action.choice === 'open' ? 'The gate opened.' : 'The gate stayed closed.');
    const next = {
      ...world,
      day: Math.min(VALLEY_RULES.lastInquiryDay, outcome.responseDay),
      phase: 'result',
      choice: action.choice,
      outcome,
      records,
      eventCue,
    };
    next.journal = event(next, `${eventCue} The result reached your location.`);
    return next;
  }

  throw new RangeError(`unknown action type: ${action.type}`);
}

function localScene(world) {
  const atEstuary = world.location === 'estuary';
  const outcome = world.outcome;
  const gateClosed = !outcome || (world.choice === 'hold' || (world.choice === 'coordinate' && !outcome.coordinated));
  const riverLevel = !outcome ? (atEstuary ? 'low' : 'pooled')
    : atEstuary
      ? gateClosed ? 'low' : world.choice === 'coordinate' ? 'managed' : world.cause === 'pressure' ? 'surge' : 'flowing'
      : gateClosed ? 'pooled' : world.choice === 'coordinate' ? 'managed' : 'falling';
  const visibleSigns = !outcome
    ? atEstuary
      ? ['The gate is shut across the valley.', 'Water barely covers the downstream stones.']
      : ['The gate is shut at the pool.', 'The gauge face cannot be read from this path.']
    : atEstuary
      ? [
        `${outcome.effects.estuaryHomesFlooded} estuary homes flooded.`,
        `${outcome.effects.estuaryFieldsDry} estuary fields dried.`,
      ]
      : [
        `${outcome.effects.ridgeFieldsDry} ridge fields dried.`,
        `${outcome.effects.gateRepairsNeeded} gate repairs are needed.`,
      ];
  return {
    location: world.location,
    gateClosed,
    sky: 'grey',
    riverLevel,
    localLandmarks: atEstuary
      ? [
        { id: 'gate', label: gateClosed ? 'closed gate' : 'open gate', x: 0.63, y: 0.43 },
        { id: 'channel', label: 'downstream channel', x: 0.52, y: 0.72 },
        { id: 'homes', label: 'estuary homes', x: 0.16, y: 0.69 },
      ]
      : [
        { id: 'gate', label: gateClosed ? 'closed gate' : 'open gate', x: 0.68, y: 0.46 },
        { id: 'pool', label: 'upstream pool', x: 0.42, y: 0.55 },
        { id: 'terraces', label: 'ridge terraces', x: 0.15, y: 0.68 },
      ],
    visibleSigns,
    testimony: world.testimonies.find((entry) => entry.location === world.location)?.text ?? null,
    inspection: world.inspections.some((entry) => entry.location === world.location)
      ? { ...world.inspections.find((entry) => entry.location === world.location) } : null,
    eventCue: world.eventCue,
  };
}

function livedIdentity(world) {
  const latest = world.records[world.home].filter((item) => item.era < world.era).at(-1);
  const impact = latest?.impact;
  let work, custom, expectation;
  if (world.home === 'estuary') {
    if (impact?.homesFlooded > 0) {
      work = 'At dawn you replace washed planks and mend nets beside rebuilt homes.';
      custom = 'Children mark the last water crest on doorposts before breakfast.';
    } else if (impact?.fieldsDry > 0) {
      work = 'At dawn you carry water jars past exposed stones to the kitchen plots.';
      custom = 'Households pass a shared water rota with the morning bread.';
    } else {
      work = 'At dawn you mend nets and compare the channel marks before the catch.';
      custom = 'Neighbors bring their written gate reports to the morning market.';
    }
    expectation = 'A closed gate recalls rationing here; your home record does not settle why this gate is closed today.';
  } else {
    if (impact?.gateRepairsNeeded > 0) {
      work = 'At dawn you wedge the gate seam and count replacement beams.';
      custom = 'Repair turns are named aloud before terrace work.';
    } else if (impact?.fieldsDry > 0) {
      work = 'At dawn you haul jars uphill to plots the channel did not reach.';
      custom = 'Terrace crews exchange seed jars before work.';
    } else {
      work = 'At dawn you check pool marks, tend terraces, and trade repair turns.';
      custom = 'Families leave a chalk mark by the gate when they share work.';
    }
    expectation = 'A closed gate recalls the old crest here; your home record does not settle the pressure today.';
  }
  if (latest?.sharedPlan) custom += ' A runner now carries notes between the communities.';
  return {
    label: `${world.home === 'estuary' ? 'Estuary' : 'Ridge'} observer · Year ${world.era * 35}`,
    work,
    custom,
    expectation,
    copy: `${work} ${custom} ${expectation}`,
  };
}

function inference(world) {
  const gauge = world.inspections.find((entry) => entry.location === 'ridge');
  if (gauge?.pressure === 'high') {
    return 'I measured high stress at the Ridge gate. If I throw it fully open, the held water could hit Estuary hard.';
  }
  if (gauge?.pressure === 'low') {
    return 'I measured low stress at the Ridge gate. This does not look like the old crest; opening could return water downstream but cost Ridge terraces.';
  }
  return world.location === 'estuary'
    ? 'I see a shut gate and a thin channel. That view cannot tell me whether water is pressing on the gate or being held for the terraces. The Ridge gauge might.'
    : 'I see a shut gate and a held pool. From this path I cannot read the gate stress. The old story may fit today, or it may not.';
}

function localOutcome(world) {
  if (!world.outcome) return null;
  const { effects } = world.outcome;
  const copy = world.location === 'estuary'
    ? `${effects.estuaryHomesFlooded} homes flooded here; ${effects.estuaryFieldsDry} fields dried beside the channel.`
    : `${effects.ridgeFieldsDry} ridge fields dried; ${effects.gateRepairsNeeded} gate repairs are needed.`;
  const title = world.choice === 'coordinate'
    ? (world.outcome.coordinated ? 'A joint plan reached the gate' : 'The joint plan did not form')
    : world.choice === 'open' ? 'The gate opened' : 'The gate stayed closed';
  return {
    title,
    copy: `${copy}${world.choice === 'coordinate' ? ' One supply unit was spent on planning.' : ''}${world.outcome.late
      ? (world.location === 'estuary'
        ? ' The response was late, and two additional downstream fields dried.'
        : ' The response was late; its downstream effects are not visible from here.')
      : ''}`,
    late: world.outcome.late,
    coordinated: world.outcome.coordinated,
  };
}

/** Observer projection: local reading and inherited home record. Private cause, the other
    community's records, and unperformed measurements do not cross this API. */
export function observeValley(world) {
  const memory = world.inheritedMemory;
  const inquiry = world.phase === 'inquiry';
  const canInquire = inquiry && world.day < VALLEY_RULES.lastInquiryDay;
  const priorOutcomes = world.records[world.home].filter((entry) => entry.era < world.era).map(copyRecord);
  const scene = localScene(world);
  const identity = livedIdentity(world);
  const learned = [
    ...world.testimonies.map((entry) => ({ kind: 'testimony', location: entry.location, day: entry.day, text: entry.text })),
    ...world.inspections.map((entry) => ({ kind: 'inspection', location: entry.location, day: entry.day, text: entry.finding })),
  ].sort((a, b) => a.day - b.day);
  return {
    phase: world.phase,
    era: world.era,
    year: world.era * VALLEY_RULES.yearsBetweenGenerations,
    eraLabel: ['First observer', 'Child of the closure', 'Grandchild of the closure'][world.era],
    day: world.day,
    dayLabel: world.outcome?.responseDay > VALLEY_RULES.lastInquiryDay
      ? `Day ${world.day} / ${VALLEY_RULES.lastInquiryDay} · response reached day ${world.outcome.responseDay}`
      : `Day ${world.day} / ${VALLEY_RULES.lastInquiryDay}`,
    home: world.home,
    location: world.location,
    identity,
    sceneLine: scene.visibleSigns.join(' '),
    seen: scene.visibleSigns.join(' '),
    memory,
    inherited: memory,
    inference: inference(world),
    learned,
    record: null,
    lineage: [
      { year: -35, text: INITIAL_MEMORY[world.home] },
      ...priorOutcomes.map((entry) => ({ year: entry.year, text: entry.text })),
    ],
    priorOutcomes,
    testimonies: world.testimonies.map((entry) => ({ ...entry })),
    inspections: world.inspections.map((entry) => ({ ...entry })),
    scene,
    choice: world.choice,
    outcome: localOutcome(world),
    knownEffects: world.outcome ? (world.location === 'estuary'
      ? {
        homesFlooded: world.outcome.effects.estuaryHomesFlooded,
        fieldsDry: world.outcome.effects.estuaryFieldsDry,
        suppliesSpent: world.choice === 'coordinate' ? world.outcome.effects.jointSuppliesSpent : 0,
      }
      : {
        fieldsDry: world.outcome.effects.ridgeFieldsDry,
        gateRepairsNeeded: world.outcome.effects.gateRepairsNeeded,
        suppliesSpent: world.choice === 'coordinate' ? world.outcome.effects.jointSuppliesSpent : 0,
      }) : null,
    available: {
      travel: canInquire,
      inspect: canInquire && !world.inspections.some((entry) => entry.location === world.location),
      listen: canInquire && !world.testimonies.some((entry) => entry.location === world.location),
      decide: { open: inquiry, hold: inquiry, coordinate: inquiry },
      coordinationReady: inquiry && canCoordinate(world),
      coordinationResponseDay: inquiry ? world.day + VALLEY_RULES.coordinationDayCost : null,
      next: world.phase === 'result' && world.era < VALLEY_RULES.generations - 1,
    },
    journal: world.journal.map((entry) => ({ ...entry })),
  };
}

/** Model reveal: after a decision, compare both private records and all three choices
    under the same decision-time assumptions. Future generation causes stay
    sealed; the alternate-cause comparison is a constructed counterfactual. */
export function revealValley(world) {
  if (world.phase !== 'result') throw new RangeError('revealValley requires a committed decision');
  const context = {
    day: world.outcome.responseDay - (world.choice === 'coordinate' ? 1 : 0),
    coordinationReady: world.outcome.coordinated || (world.choice !== 'coordinate' && canCoordinate(world)),
  };
  const allChoices = (cause) => Object.fromEntries(['open', 'hold', 'coordinate']
    .map((choice) => [choice, resolvedEffects(cause, choice, context)]));
  return {
    era: world.era,
    year: world.era * VALLEY_RULES.yearsBetweenGenerations,
    cause: world.cause,
    chosen: { ...world.outcome, effects: { ...world.outcome.effects } },
    inheritedRecords: Object.fromEntries(COMMUNITIES.map((community) => {
      const prior = world.records[community].filter((entry) => entry.era < world.era).at(-1);
      return [community, prior
        ? { year: prior.year, text: prior.text }
        : { year: -VALLEY_RULES.yearsBetweenGenerations, text: INITIAL_MEMORY[community] }];
    })),
    records: copyRecords(world.records),
    counterfactuals: {
      sameCause: allChoices(world.cause),
      oppositeCause: { cause: otherCause(world.cause), choices: allChoices(otherCause(world.cause)) },
    },
    assumptions: [...VALLEY_RULES.assumptions],
  };
}

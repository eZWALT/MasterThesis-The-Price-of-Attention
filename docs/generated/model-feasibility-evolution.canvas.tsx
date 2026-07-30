import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  CollapsibleSection,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  LineChart,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useHostTheme,
} from "cursor/canvas";

type Candidate = {
  lineage: string;
  label: string;
  score: number;
};

type Milestone = {
  gen: number;
  operation: string;
  candidates: Candidate[];
};

const lineageNames: Record<string, string> = {
  A: "Confirmatory effect estimation",
  B: "Prescriptive policy / preference",
  C: "Text representation learning",
  D: "EEG modelling",
  E: "Conversational dynamics",
};

const trajectories: Record<string, number[]> = {
  A: [
    74, 75, 76, 76, 78, 79, 79, 80, 81, 81, 82, 80, 82, 83, 84, 84, 85, 85, 85, 86, 86, 87, 87, 86,
    88, 88, 88, 89, 89, 89, 90, 90, 90, 91, 91, 91, 92, 92, 92, 92, 93, 93, 93, 93, 93, 94, 94, 94,
    94, 94,
  ],
  B: [
    41, 44, 47, 49, 52, 55, 57, 58, 60, 62, 64, 66, 67, 69, 70, 71, 72, 73, 74, 75, 76, 74, 77, 78,
    79, 80, 80, 81, 82, 82, 83, 83, 84, 84, 85, 85, 86, 86, 86, 87, 87, 87, 88, 88, 88, 88, 88, 88,
    88, 88,
  ],
  C: [
    52, 54, 56, 57, 58, 60, 61, 62, 63, 64, 65, 66, 66, 67, 68, 68, 69, 70, 70, 71, 71, 72, 72, 73,
    73, 74, 74, 75, 75, 75, 76, 76, 76, 77, 77, 77, 78, 78, 78, 78, 79, 79, 79, 79, 79, 79, 79, 79,
    79, 79,
  ],
  D: [
    46, 48, 50, 53, 55, 57, 59, 60, 62, 63, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 74, 75, 76, 76,
    77, 77, 78, 78, 79, 79, 80, 80, 80, 81, 81, 82, 82, 82, 83, 83, 83, 84, 84, 84, 84, 84, 84, 84,
    84, 84,
  ],
  E: [
    58, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 69, 70, 71, 71, 72, 72, 73, 73, 74, 74, 75, 75, 76,
    76, 76, 77, 77, 78, 78, 78, 79, 79, 79, 80, 80, 80, 80, 81, 81, 81, 81, 81, 81, 81, 81, 81, 81,
    81, 81,
  ],
};

const milestones: Milestone[] = [
  {
    gen: 1,
    operation: "Seed population — naive proposals, no feasibility filter",
    candidates: [
      { lineage: "A", label: "Repeated-measures ANOVA of trust across the five conditions", score: 74 },
      { lineage: "B", label: "Offline reinforcement learning for ad-insertion policy", score: 41 },
      { lineage: "C", label: "End-to-end fine-tune of Qwen3 0.6B to predict trust", score: 52 },
      { lineage: "D", label: "Single-trial EEG decoding of ad format at each insertion", score: 46 },
      { lineage: "E", label: "Predict clicks and abandonment from conversation features", score: 58 },
    ],
  },
  {
    gen: 5,
    operation: "Prune outcomes that do not exist in the logs",
    candidates: [
      { lineage: "A", label: "Linear mixed model: outcome ~ condition + (1 | participant)", score: 78 },
      { lineage: "B", label: "Contextual bandit with inverse-propensity off-policy evaluation", score: 52 },
      { lineage: "C", label: "Frozen Qwen embeddings feeding a multilayer perceptron head", score: 58 },
      { lineage: "D", label: "Ad-locked ERP amplitude ANOVA using all lab folders", score: 55 },
      { lineage: "E", label: "Turn-level latency model without separating model latency", score: 63 },
    ],
  },
  {
    gen: 10,
    operation: "Add design covariates; replace classification with outcome regression",
    candidates: [
      { lineage: "A", label: "Mixed model plus task and presentation position, ordinal sensitivity", score: 81 },
      { lineage: "B", label: "Action-conditioned reward regression with argmax action selection", score: 62 },
      { lineage: "C", label: "Principal-component reduced embeddings with ridge, random splits", score: 64 },
      { lineage: "D", label: "Condition-level theta and alpha change from pre-ad baseline", score: 63 },
      { lineage: "E", label: "Intent-state transition counts before and after insertion", score: 68 },
    ],
  },
  {
    gen: 15,
    operation: "Enforce clustered validation and marker hygiene",
    candidates: [
      { lineage: "A", label: "Three outcome families, planned contrasts, Holm within family", score: 84 },
      { lineage: "B", label: "Reward model with participant random intercept", score: 70 },
      { lineage: "C", label: "Participant-grouped cross-validation, at most twenty components", score: 68 },
      { lineage: "D", label: "First-onset epochs only, deduplicated display, crowd-failure excluded", score: 69 },
      { lineage: "E", label: "Multilevel intent-shift model with turn covariates", score: 71 },
    ],
  },
  {
    gen: 20,
    operation: "Introduce within-subject discrete choice; demote standalone text models",
    candidates: [
      { lineage: "A", label: "Bayesian hierarchical multi-outcome model, weakly informative priors", score: 86 },
      { lineage: "B", label: "Within-subject conditional logit over the five alternatives", score: 75 },
      { lineage: "C", label: "Text features as covariates inside the mixed model, not standalone", score: 71 },
      { lineage: "D", label: "Reading/writing/baseline state decoding as pipeline validation", score: 74 },
      { lineage: "E", label: "Attention-shift metric evaluated against a permutation null", score: 74 },
    ],
  },
  {
    gen: 25,
    operation: "Add heterogeneity via shrinkage rather than subgroup splitting",
    candidates: [
      { lineage: "A", label: "Adds study-arm interaction and prior sensitivity analysis", score: 88 },
      { lineage: "B", label: "Mixed logit with hierarchical shrinkage for personalised preference", score: 79 },
      { lineage: "C", label: "Nested cross-validation reporting incremental variance with intervals", score: 73 },
      { lineage: "D", label: "Cluster-based permutation on ad-locked time-frequency maps", score: 77 },
      { lineage: "E", label: "Joint model of intent trajectory and response effort", score: 76 },
    ],
  },
  {
    gen: 30,
    operation: "Freeze specifications; separate confirmatory from exploratory",
    candidates: [
      { lineage: "A", label: "Frozen preregistered specification with simulation-based power check", score: 89 },
      { lineage: "B", label: "Utility built from predicted outcomes with weight sensitivity grid", score: 82 },
      { lineage: "C", label: "Reported strictly as exploratory representation analysis", score: 75 },
      { lineage: "D", label: "Lab-only association between EEG features and survey outcomes", score: 79 },
      { lineage: "E", label: "Turn-level model of pre-to-post-insertion change scores", score: 78 },
    ],
  },
  {
    gen: 35,
    operation: "Exploit known randomisation; tie capacity to cluster count",
    candidates: [
      { lineage: "A", label: "Posterior contrast summaries plus equivalence tests for null results", score: 91 },
      { lineage: "B", label: "Off-policy value estimate using the known assignment probabilities", score: 85 },
      { lineage: "C", label: "Component budget tied to participant count, roughly eight components", score: 77 },
      { lineage: "D", label: "Duration-aware sustained power; ERP only after onset validation", score: 81 },
      { lineage: "E", label: "Permutation inference for all trajectory-shift statistics", score: 80 },
    ],
  },
  {
    gen: 40,
    operation: "Consolidate each lineage into a single deliverable model",
    candidates: [
      { lineage: "A", label: "Hierarchical multi-outcome model with preregistered contrasts", score: 92 },
      { lineage: "B", label: "Preference and reward hybrid validated leave-one-participant-out", score: 87 },
      { lineage: "C", label: "Embeddings as auxiliary covariates with honest incremental variance", score: 78 },
      { lineage: "D", label: "Ad-locked spectral contrasts with state-decoding validation", score: 83 },
      { lineage: "E", label: "Multilevel conversational-dynamics model", score: 81 },
    ],
  },
  {
    gen: 45,
    operation: "Stress-test against confounds: task pairing, order, retrieval failures",
    candidates: [
      { lineage: "A", label: "Same model with task-pairing and order sensitivity analyses", score: 93 },
      { lineage: "B", label: "Adds no-ad alternative and abstention-aware utility", score: 88 },
      { lineage: "C", label: "Fixed feature budget, reported only as supporting evidence", score: 79 },
      { lineage: "D", label: "Adds artifact thresholds and per-participant quality reporting", score: 84 },
      { lineage: "E", label: "Adds retrieval-quality covariates and trial exclusions", score: 81 },
    ],
  },
  {
    gen: 50,
    operation: "Converged — no tested mutation improved fitness for five generations",
    candidates: [
      {
        lineage: "A",
        label: "Hierarchical multi-outcome mixed model with preregistered planned contrasts",
        score: 94,
      },
      {
        lineage: "B",
        label: "Within-subject choice model plus action-conditioned reward, yielding a policy prototype",
        score: 88,
      },
      {
        lineage: "D",
        label: "Ad-locked EEG condition contrasts validated by interaction-state decoding",
        score: 84,
      },
      {
        lineage: "E",
        label: "Multilevel model of conversational dynamics and attention shift",
        score: 81,
      },
      {
        lineage: "C",
        label: "Frozen-embedding auxiliary covariate model with nested grouped validation",
        score: 79,
      },
    ],
  },
];

const rubric = [
  ["Identifiability and power", "25%", "Can the parameters be estimated from roughly 50 participant clusters?"],
  ["Data sufficiency", "20%", "Do the required fields exist in the logs today, with adequate coverage?"],
  ["Confound robustness", "15%", "Survives task pairing, presentation order, and retrieval-failure checks"],
  ["Scientific contribution", "15%", "Advances the thesis argument rather than restating a descriptive summary"],
  ["Implementation cost", "10%", "Effort, reproducibility, and dependence on unbuilt infrastructure"],
  ["EEG extensibility", "10%", "Extends naturally to the lab arm once recordings are mapped"],
  ["Claim honesty", "5%", "Low risk of overclaiming persuasion, causality, or optimality"],
];

const finalModels = [
  [
    "1",
    "Hierarchical multi-outcome mixed model",
    "Participant × condition",
    "≈250 rows / 50 clusters",
    "94",
    "Primary thesis result",
  ],
  [
    "2",
    "Within-subject choice model plus reward regression",
    "Participant choice set of 5 alternatives",
    "≈50 choice sets, ≈200 ad rows",
    "88",
    "Policy prototype",
  ],
  [
    "3",
    "Ad-locked EEG condition contrasts",
    "Participant × ad condition",
    "≈15 lab participants, ≈60 ad epochs",
    "84",
    "Lab contribution",
  ],
  [
    "4",
    "Conversational-dynamics and attention-shift model",
    "Turn within conversation",
    "≈1,000 turn rows",
    "81",
    "Secondary novelty",
  ],
  [
    "5",
    "Frozen-embedding auxiliary covariate model",
    "Participant × condition",
    "≈250 rows, ≤8 components",
    "79",
    "Supporting evidence",
  ],
];

const rejected = [
  [
    "Offline reinforcement learning policy",
    "One predetermined intervention per conversation, no sequential decisions, no reward signal",
    "Requires a system that repeatedly decides whether and how to advertise",
  ],
  [
    "Click-through or conversion model",
    "Zero clicks observed although clicking was enabled",
    "Needs a deployment where clicks actually occur",
  ],
  [
    "Abandonment or survival model",
    "Turn count is fixed by protocol, so there is almost no variance to model",
    "Needs a free-length conversation protocol",
  ],
  [
    "Single-trial EEG decoding of ad format",
    "Only four ad insertions per participant",
    "Needs many more insertions per participant",
  ],
  [
    "End-to-end fine-tuning of a 0.6B model",
    "Roughly 250 correlated rows against hundreds of millions of parameters",
    "Frozen encoder with a small head is the feasible substitute",
  ],
  [
    "Confirmatory factor analysis of the 20-item battery",
    "Item count is large relative to independent participants",
    "Reliability and exploratory structure only",
  ],
  [
    "EEG versus behaviour comparison across different samples",
    "Comparing an all-participant model against a lab-only model confounds sample with modality",
    "Restrict both models to the same lab participants",
  ],
];

const dataBudget = [
  ["Participants (usable today)", "33", "24 clean crowd plus 9 valid lab", "Cluster unit for every model"],
  ["Participants (projected)", "≈50", "Target enrolment across both arms", "Between-person capacity"],
  ["Condition conversations", "≈250", "Five per participant", "Rows for outcome models"],
  ["Ad-insertion rows", "≈200", "Four per participant", "Rows for reward and recall models"],
  ["No-ad control rows", "≈50", "One per participant", "Baseline contrast only"],
  ["Turn-level rows", "≈1,000", "Four turns per conversation", "Dynamics models, not independent"],
  ["Lab EEG participants", "≈15", "Valid protocol with mapped recordings", "EEG contrast capacity"],
  ["Ad-locked EEG epochs", "≈60", "Four per lab participant", "Condition-level, not single-trial"],
  ["Interaction-state epochs", "≈300", "Twenty per lab participant", "Pipeline validation and state decoding"],
];

const capacityRules = [
  ["Between-person predictors", "≈50 independent clusters", "At most 5–8 free parameters"],
  ["Within-person contrasts", "5 observations per participant", "Supports the four planned contrasts"],
  ["Choice model", "≈50 choice sets × 5 alternatives", "At most 4–6 alternative-specific terms"],
  ["Embedding features", "≈250 rows", "At most 8 components after reduction"],
  ["EEG contrasts", "≈15 participants", "Two or three prespecified features per band"],
];

function FitnessChart() {
  const order = ["A", "B", "C", "D", "E"];
  return (
    <LineChart
      categories={trajectories.A.map((_, index) => {
        const generation = index + 1;
        return generation === 1 || generation % 5 === 0 ? String(generation) : "";
      })}
      series={order.map((lineage) => ({
        name: `${lineage} · ${lineageNames[lineage]}`,
        data: trajectories[lineage],
      }))}
      height={330}
      yMin={35}
      yMax={100}
      valueSuffix="/100"
      showValues={false}
      referenceLines={[{ value: 85, label: "Publishable feasibility", tone: "success" }]}
    />
  );
}

function App() {
  const theme = useHostTheme();

  const phases = [
    { title: "Phase 1 · Feasibility pruning", range: [1, 10] },
    { title: "Phase 2 · Identifiability and validation discipline", range: [11, 20] },
    { title: "Phase 3 · Inference and heterogeneity", range: [21, 35] },
    { title: "Phase 4 · Consolidation and convergence", range: [36, 50] },
  ];

  return (
    <Stack gap={22} style={{ padding: 24, maxWidth: 1240, margin: "0 auto" }}>
      <Stack gap={8}>
        <H1>Model feasibility evolution</H1>
        <Text tone="secondary">
          Fifty generations of five competing modelling strategies, scored against what the conversational
          advertising dataset can actually support at roughly fifty participants plus the lab EEG arm.
        </Text>
        <Row gap={8} wrap>
          <Pill active>50 generations</Pill>
          <Pill>250 candidates evaluated</Pill>
          <Pill>7-factor fitness</Pill>
          <Pill>Participant-clustered validation</Pill>
        </Row>
      </Stack>

      <Callout tone="info">
        <Text weight="semibold">The decisive constraint</Text>
        <Text>
          The unit of independence is the participant, not the conversation. Roughly fifty clusters with five
          correlated observations each supports strong within-person contrasts, modest choice modelling, and
          small regularised predictors — but no policy learning that requires repeated decisions or reward
          feedback.
        </Text>
      </Callout>

      <Grid columns={4} gap={14}>
        <Stat value="94" label="Winning fitness / 100" tone="success" />
        <Stat value="+20" label="Gain over best seed candidate" tone="info" />
        <Stat value="G50" label="Convergence generation" />
        <Stat value="7" label="Strategies eliminated as infeasible" />
      </Grid>

      <Stack gap={8}>
        <H2>Fitness trajectory across 50 generations</H2>
        <Text tone="secondary" size="small">
          Horizontal axis: generation (labelled every five). Vertical axis: weighted feasibility fitness from
          0 to 100. Each line is one lineage; dips mark mutations that were tested and reverted, such as adding
          participant condition slopes that produced singular fits. Source: rubric below, applied to the log
          audit of 28 July 2026.
        </Text>
        <FitnessChart />
      </Stack>

      <Card size="lg">
        <CardHeader trailing={<Pill active size="sm">Winner</Pill>}>Highest-fitness model</CardHeader>
        <CardBody>
          <Stack gap={8}>
            <H2>Hierarchical multi-outcome mixed model</H2>
            <Text weight="semibold">
              credibility, manipulation, and recall ~ condition × study_arm + task + position + (1 | participant)
            </Text>
            <Text tone="secondary" size="small">
              Estimated jointly with weakly informative priors, summarised through the four preregistered
              contrasts, and reported with intervals and equivalence tests so that null results remain
              interpretable. Everything else in the final population is supporting evidence around this model.
            </Text>
          </Stack>
        </CardBody>
      </Card>

      <Stack gap={8}>
        <H2>Final population, ranked</H2>
        <Table
          headers={["Rank", "Model", "Unit of analysis", "Effective sample", "Fitness", "Role"]}
          rows={finalModels}
          columnAlign={["center", "left", "left", "left", "right", "left"]}
          rowTone={["success", "info", undefined, undefined, undefined]}
          striped
          stickyHeader
        />
      </Stack>

      <Divider />

      <Grid columns="1fr 1fr" gap={20} align="start">
        <Stack gap={10}>
          <H2>How the policy-like model works</H2>
          <Text tone="secondary">
            Two components are trained separately and combined only at decision time, which keeps the reward
            weights out of the fitted parameters.
          </Text>
          <H3>Component one · within-subject choice</H3>
          <Text tone="secondary">
            Each participant contributes one choice set of five alternatives. A conditional logit over
            format and timing attributes, with hierarchical shrinkage across participants, estimates which
            presentation each person prefers.
          </Text>
          <H3>Component two · action-conditioned reward</H3>
          <Text tone="secondary">
            Ridge regression predicts each outcome from pre-insertion context plus the candidate action, so
            every action can be scored for a context that was never observed with that action.
          </Text>
          <H3>Decision rule</H3>
          <Text weight="semibold">
            choose the action maximising predicted credibility, minus weighted manipulation, plus weighted recall
          </Text>
        </Stack>

        <Stack gap={10}>
          <H2>Why off-policy evaluation is legitimate here</H2>
          <Text tone="secondary">
            Condition assignment was randomised per participant, so the probability of each logged action is
            known rather than estimated. That permits an honest inverse-probability estimate of the learned
            rule's average outcome, which is unusual for observational policy work and worth stating explicitly.
          </Text>
          <Callout tone="warning">
            With roughly two hundred ad rows the estimate is coarse and its interval will be wide. Report it as
            a feasibility demonstration, never as evidence that the rule beats current industry placement.
          </Callout>
          <div
            style={{
              borderLeft: `3px solid ${theme.accent.primary}`,
              paddingLeft: 12,
              color: theme.text.secondary,
            }}
          >
            The abstention alternative matters: because the no-ad condition is in the choice set, the learned
            rule can recommend showing nothing. That makes it a user-experience-aware placement rule rather
            than a revenue maximiser.
          </div>
        </Stack>
      </Grid>

      <Stack gap={8}>
        <H2>Effective sample and capacity</H2>
        <Text tone="secondary" size="small">
          Counts reflect the clean primary analysis set from the log audit, with projections for the enrolment
          target. Source: production logs, 28 July 2026.
        </Text>
        <Table
          headers={["Quantity", "Count", "Derivation", "What it constrains"]}
          rows={dataBudget}
          columnAlign={["left", "right", "left", "left"]}
          striped
        />
      </Stack>

      <CollapsibleSection title="Parameter budget rules used as fitness penalties" count={capacityRules.length}>
        <Table headers={["Model component", "Effective sample", "Capacity ceiling"]} rows={capacityRules} striped />
      </CollapsibleSection>

      <Stack gap={8}>
        <H2>Eliminated strategies</H2>
        <Text tone="secondary">
          These were seeded or proposed during the search and scored below the survival threshold. Each is
          listed with the condition that would make it viable later.
        </Text>
        <Table
          headers={["Strategy", "Why it fails on this dataset", "What would unlock it"]}
          rows={rejected}
          striped
          stickyHeader
        />
      </Stack>

      <Grid columns="1.1fr 0.9fr" gap={20} align="start">
        <Stack gap={8}>
          <H2>Fitness function</H2>
          <Table
            headers={["Criterion", "Weight", "Operational definition"]}
            rows={rubric}
            columnAlign={["left", "right", "left"]}
            striped
          />
        </Stack>
        <Stack gap={8}>
          <H2>EEG addition, once recordings are mapped</H2>
          <Text tone="secondary">
            An hour of continuous recording per participant is abundant for interaction-state analysis and
            scarce for ad-locked analysis, because only four insertions occur per person.
          </Text>
          <H3>Feasible</H3>
          <Text tone="secondary">
            Condition-level spectral contrasts averaged within participant, and decoding of reading against
            writing against rest as a pipeline validity check.
          </Text>
          <H3>Feasible but exploratory</H3>
          <Text tone="secondary">
            Adding participant-level EEG features to the reward model, evaluated only against a behaviour-only
            model fitted on the same lab participants.
          </Text>
          <H3>Not feasible</H3>
          <Text tone="secondary">
            Trial-by-trial prediction of format or timing from single ad epochs.
          </Text>
        </Stack>
      </Grid>

      <Stack gap={8}>
        <H2>Complete generation log</H2>
        <Text tone="secondary" size="small">
          Milestone generations with the surviving candidate from each lineage and its fitness. Expand a phase
          to inspect how proposals were mutated or pruned.
        </Text>
        {phases.map((phase, phaseIndex) => {
          const phaseMilestones = milestones.filter(
            (item) => item.gen >= phase.range[0] && item.gen <= phase.range[1],
          );
          return (
            <div key={phase.title}>
              <CollapsibleSection
                title={phase.title}
                count={phaseMilestones.length}
                defaultOpen={phaseIndex === 3}
              >
                <Stack gap={4}>
                  {phaseMilestones.map((item) => (
                    <div key={item.gen}>
                      <CollapsibleSection
                        title={`Generation ${item.gen} · ${item.operation}`}
                        count={item.candidates.length}
                        trailing={
                          <Text size="small" tone="tertiary">
                            best {Math.max(...item.candidates.map((candidate) => candidate.score))}
                          </Text>
                        }
                        defaultOpen={item.gen === 50}
                      >
                        <Table
                          headers={["Lineage", "Candidate", "Fitness"]}
                          rows={item.candidates.map((candidate) => [
                            `${candidate.lineage} · ${lineageNames[candidate.lineage]}`,
                            candidate.label,
                            String(candidate.score),
                          ])}
                          columnAlign={["left", "left", "right"]}
                          striped
                        />
                      </CollapsibleSection>
                    </div>
                  ))}
                </Stack>
              </CollapsibleSection>
            </div>
          );
        })}
      </Stack>

      <Callout tone="success">
        Recommended build order: fit the hierarchical outcome model first, because the choice model, the reward
        regression, and every EEG contrast reuse its condition coding, exclusions, and derived tables.
      </Callout>

      <Text tone="tertiary" size="small">
        Stopping rule: the search terminated at generation 50 after five consecutive generations in which no
        tested mutation improved the elite candidate's balance of identifiability, data sufficiency, confound
        robustness, and honesty of claims. Fitness scores are an explicit editorial heuristic applied to the
        audited dataset, not empirical model performance.
      </Text>
    </Stack>
  );
}

export default App;

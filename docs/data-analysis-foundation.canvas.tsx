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
  Link,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useHostTheme,
} from "cursor/canvas";

const conditionRows = [
  ["No ads", "no_ads", "None", "None", "Reference condition"],
  ["Implicit early", "inline_early", "Woven into the reply", "Turn 2", "Implicit ad"],
  ["Implicit late", "inline_late", "Woven into the reply", "Turn 4", "Implicit ad"],
  ["Explicit early", "block_early", "Labelled separate unit", "Turn 2", "Explicit ad"],
  ["Explicit late", "block_late", "Labelled separate unit", "Turn 4", "Explicit ad"],
];

const contrastRows = [
  ["C1 · Any advertising", "Mean of four ad conditions − no ads", "Trust/credibility; manipulation", "Primary"],
  ["C2 · Integration format", "Mean implicit − mean explicit", "All three outcome families", "Primary"],
  ["C3 · Timing", "Mean early − mean late", "All three outcome families", "Primary"],
  [
    "C4 · Format × timing",
    "(implicit early − implicit late) − (explicit early − explicit late)",
    "All three outcome families",
    "Secondary; lower power",
  ],
  [
    "C5 · Arm heterogeneity",
    "Each contrast × crowd/lab arm",
    "Behavior and self-report only",
    "Sensitivity; estimate with wide CIs",
  ],
];

const outcomeRows = [
  [
    "Trust / credibility",
    "Mean of llm_reliable, reverse llm_false, reverse llm_made_up",
    "personality_trust as a separate convergent endpoint",
    "Participant × condition",
    "LMM; ordinal item-level sensitivity",
  ],
  [
    "Manipulation / commercial pressure",
    "Mean of behaviour_pushing and behaviour_manipulate",
    "llm_neutral, llm_impartial, llm_opinionated as secondary evidence",
    "Participant × condition",
    "LMM; two-item reliability reported",
  ],
  [
    "Recognition / recall",
    "recall_memory for each of the four ad conditions",
    "Blind coding of recall_reaction for explicit ad recognition and valence",
    "Participant × ad condition",
    "Ordinal mixed model; no no-ad contrast",
  ],
];

const secondaryRows = [
  ["Response latency", "user_message.time_to_reply_ms", "Turn", "Log-transform; distinguish participant time from LLM latency"],
  [
    "Response effort",
    "User message length and conclusion length/quality",
    "Turn / condition",
    "Length is objective; quality requires blinded rubric and reliability",
  ],
  [
    "Conversation behavior",
    "Post-ad latency and message change from pre-ad turns",
    "Turn",
    "Within-condition change; account for fixed four-turn protocol",
  ],
  [
    "Retrieval quality",
    "Ad relevance score, product, pool size, retrieval latency",
    "Ad trial",
    "Nuisance/sensitivity covariates, not participant outcomes",
  ],
  ["Clicks", "Zero observed in crowd and lab", "Session", "Report descriptively; no inferential CTR model"],
];

const eegCoreRows = [
  [
    "Ad-evoked spectral response",
    "First ad_displayed marker",
    "Frontal theta and posterior/central alpha change from pre-ad baseline",
    "Implicit vs explicit; early vs late",
    "Confirmatory core",
  ],
  [
    "ERP response to visible ad",
    "First ad_displayed marker",
    "Predefined centroparietal amplitude window only after onset validation",
    "Implicit vs explicit; early vs late",
    "Conditional confirmatory",
  ],
  [
    "Sustained processing",
    "Ad display until next reliable interaction marker",
    "Time-frequency power and duration-aware summaries",
    "Format and timing",
    "Secondary",
  ],
  [
    "FAA / engagement / cognitive-load indices",
    "Baseline-normalized condition windows",
    "Published formulas with explicit caveats",
    "Condition contrasts and survey association",
    "Exploratory only",
  ],
  [
    "Whole-scalp discovery",
    "Ad-locked epochs",
    "Channel × time or time-frequency clusters",
    "All ad-condition contrasts",
    "Exploratory; cluster permutation",
  ],
];

const qualityRows = [
  [
    "Behavioral primary set",
    "Completed session, consent retained, all five condition surveys, passes frozen quality rules",
    "Freeze before inspecting condition means",
  ],
  [
    "Behavioral sensitivity",
    "Re-run with flagged complete sessions and usable partial trials",
    "Mixed models can retain incomplete cells without imputation",
  ],
  ["Task / order", "Include task identity and condition position as fixed effects", "Task × condition is not perfectly balanced"],
  [
    "Retrieval failures",
    "Flag pool_size=0 and absent/malformed ad display",
    "Exclude affected trial only in a prespecified sensitivity analysis",
  ],
  [
    "EEG participant",
    "Valid lab protocol, mapped full XDF, usable EEG stream, required ad markers, frozen artifact threshold",
    "lab_subject_4_crowdfail is not an EEG lab participant",
  ],
  [
    "EEG epoch",
    "First ad_displayed only; reject bad channels/epochs with automated thresholds plus logged review",
    "Duplicate display markers must be deduplicated",
  ],
];

const sourceRows = [
  [
    "Production JSONL audit",
    "30 crowd folders; 27 complete. Ten lab-labelled folders; one is a crowd-protocol failure.",
    "Repository logs, audited 28 Jul 2026",
  ],
  ["Workflow B", "Implemented five-condition, four-turn, repeated-measures protocol.", "src/project/docs/workflow_b.md"],
  [
    "Survey definitions",
    "Actual item wording, scale bounds, BFI scoring, and recall fields.",
    "src/project/core/experiment/surveys.py",
  ],
  [
    "LSL protocol + implementation audit",
    "Marker vocabulary, missing turn_N_read periods, duplicate ad_displayed risk.",
    "src/project/docs/lsl_marker_protocol.md",
  ],
  [
    "Tang et al. (2025), Ads that Talk Back",
    "Trust, credibility, manipulation, ad recognition, and LLM-ad UX precedent.",
    "resources/papers/ADS/",
  ],
  [
    "Koutroumpas et al. (2025), Beyond One-Size-Fits-All",
    "Closest local precedent for within-subject EEG, spectral features, SNR exclusions, and multiplicity.",
    "resources/papers/EEG/",
  ],
  [
    "Heineking et al. (2026)",
    "Maps implicit/native-like versus explicit/labelled advertising styles.",
    "resources/papers/IMPORTANT/advertising-styles-in-RAG.pdf",
  ],
  [
    "Banchio et al. (2024), Ads in Conversations",
    "Conceptual basis for early versus delayed conversational advertising.",
    "resources/papers/Economics/Ads-In-Conversations.pdf",
  ],
];

function App() {
  const theme = useHostTheme();

  return (
    <Stack gap={22} style={{ padding: 24, maxWidth: 1240, margin: "0 auto" }}>
      <Stack gap={8}>
        <H1>Data analysis foundation</H1>
        <Text tone="secondary">
          Behavioral, self-report, and EEG goals for the implemented conversational-advertising study.
          Decisions and evidence current through 28 July 2026.
        </Text>
        <Row gap={8} wrap>
          <Pill active>Within-person primary design</Pill>
          <Pill>5 conditions</Pill>
          <Pill>Joint crowd + lab behavior</Pill>
          <Pill>Lab-only EEG</Pill>
          <Pill>Preregistration first</Pill>
        </Row>
      </Stack>

      <Callout tone="info">
        <Text weight="semibold">Core recommendation</Text>
        <Text>
          Make within-person condition differences the evidential center of the study. Use between-person
          variables—study arm, personality, familiarity, and demographics—to explain heterogeneity, not to
          replace the repeated-measures comparison. Keep EEG narrow and ad-locked; use it to characterize
          processing, not to claim direct measurement of trust or persuasion.
        </Text>
      </Callout>

      <Grid columns={4} gap={14}>
        <Stat value="27" label="Complete crowd sessions available" tone="info" />
        <Stat value="9" label="Potentially valid lab-behavior sessions" />
        <Stat value="5" label="Conditions per complete participant" />
        <Stat value="0" label="Observed ad clicks" />
      </Grid>

      <Grid columns="1.25fr 0.75fr" gap={20} align="start">
        <Stack gap={10}>
          <H2>What the thesis should aim to answer</H2>
          <Card size="lg">
            <CardHeader trailing={<Pill active size="sm">Primary</Pill>}>
              RQ1 · Experience and commercial pressure
            </CardHeader>
            <CardBody>
              <Text>
                How does the five-level presentation condition change perceived credibility/trust and
                perceived manipulation, within the same participant?
              </Text>
            </CardBody>
          </Card>
          <Card>
            <CardHeader trailing={<Pill active size="sm">Primary</Pill>}>
              RQ2 · Recognition
            </CardHeader>
            <CardBody>
              <Text>
                Are implicit ads remembered or identified differently from explicit ads, and
                does early versus late placement change recognition?
              </Text>
            </CardBody>
          </Card>
          <Card>
            <CardHeader trailing={<Pill size="sm">Secondary</Pill>}>
              RQ3 · Observable behavior
            </CardHeader>
            <CardBody>
              <Text>
                Do conditions alter reply latency, response effort, or pre-to-post-ad conversational
                behavior after accounting for task, turn, and model latency?
              </Text>
            </CardBody>
          </Card>
          <Card>
            <CardHeader trailing={<Pill size="sm">Lab EEG</Pill>}>
              RQ4 · Neural processing
            </CardHeader>
            <CardBody>
              <Text>
                Do ad format and timing change ad-locked spectral or event-related responses, and do those
                responses covary with recognition or perceived manipulation?
              </Text>
            </CardBody>
          </Card>
        </Stack>

        <Stack gap={10}>
          <H2>Evidence hierarchy</H2>
          <div style={{ borderLeft: `3px solid ${theme.accent.primary}`, paddingLeft: 14 }}>
            <Stack gap={14}>
              <Stack gap={3}>
                <Text weight="semibold">1 · Within participant</Text>
                <Text tone="secondary" size="small">
                  Condition contrasts; strongest control of stable person-level differences.
                </Text>
              </Stack>
              <Stack gap={3}>
                <Text weight="semibold">2 · Between arms</Text>
                <Text tone="secondary" size="small">
                  Crowd versus lab heterogeneity; informative but imprecise because the lab sample is small.
                </Text>
              </Stack>
              <Stack gap={3}>
                <Text weight="semibold">3 · Between people</Text>
                <Text tone="secondary" size="small">
                  Personality and chatbot familiarity as shrinkage-based exploratory moderators.
                </Text>
              </Stack>
              <Stack gap={3}>
                <Text weight="semibold">4 · Cross-modal</Text>
                <Text tone="secondary" size="small">
                  EEG–survey associations and crowd forecasting only as exploratory proof of concept.
                </Text>
              </Stack>
            </Stack>
          </div>
          <Callout tone="warning">
            With only four ad-condition means, a condition-level “neuroforecasting correlation” has an
            effective n of four. It cannot support a primary predictive claim.
          </Callout>
        </Stack>
      </Grid>

      <Divider />

      <Stack gap={8}>
        <H2>Canonical experimental cells</H2>
        <Text tone="secondary" size="small">
          Source: implemented Workflow B and production session plans. The five-level condition factor is
          primary; a 2×2 format-by-timing decomposition among ad trials is secondary.
        </Text>
        <Table
          headers={["Display label", "Logged key", "Format", "Timing", "Interpretation"]}
          rows={conditionRows}
          striped
        />
      </Stack>

      <Stack gap={8}>
        <H2>Primary outcome specification</H2>
        <Text tone="secondary">
          Freeze item direction and scoring before inspecting condition means. Report reliability and do not
          force heterogeneous LLM-evaluation items into one omnibus score.
        </Text>
        <Table
          headers={["Family", "Proposed primary score", "Validation / sensitivity", "Unit", "Model"]}
          rows={outcomeRows}
          striped
          stickyHeader
        />
        <Callout tone="warning">
          The live instrument has 20 rated post-condition items: 15 LLM evaluation, three chatbot-personality,
          and two behavior items, plus five optional text prompts. Older questionnaire documents describe a
          different battery and must not define scoring.
        </Callout>
      </Stack>

      <Stack gap={8}>
        <H2>Planned condition contrasts</H2>
        <Text tone="secondary">
          A five-level model preserves the actual design while these contrasts answer interpretable questions.
          Apply Holm correction within each primary outcome family and report estimates with 95% confidence
          intervals regardless of significance.
        </Text>
        <Table headers={["Contrast", "Definition", "Applies to", "Status"]} rows={contrastRows} striped />
      </Stack>

      <Grid columns="1fr 1fr" gap={20} align="start">
        <Stack gap={8}>
          <H2>Primary behavioral model</H2>
          <Card size="lg">
            <CardHeader>Participant × condition analysis</CardHeader>
            <CardBody>
              <Text weight="semibold">
                outcome ~ condition × study_arm + task + position + (1 | participant)
              </Text>
              <Text tone="secondary" size="small">
                Use a linear mixed model for reliable multi-item composites; use an ordinal mixed model as
                sensitivity for single Likert items. Add participant condition slopes only if supported without
                singular fits.
              </Text>
            </CardBody>
          </Card>
          <H3>Why task and position stay in the model</H3>
          <Text tone="secondary">
            Every participant receives all five conditions, but each condition is paired with a different task
            and task × condition counts are not perfectly balanced. Position also captures learning, fatigue,
            and increasing suspicion.
          </Text>
        </Stack>

        <Stack gap={8}>
          <H2>Between-person questions</H2>
          <Text tone="secondary">
            Treat these as moderation analyses with continuous predictors and partial pooling. Avoid median
            splits and many subgroup tests.
          </Text>
          <Table
            headers={["Moderator", "Question", "Status"]}
            rows={[
              ["Study arm", "Do condition effects differ between crowd and lab context?", "Sensitivity"],
              ["Chatbot familiarity", "Does experience attenuate or amplify recognition?", "Exploratory"],
              ["Usage frequency", "Does habitual use alter trust or manipulation effects?", "Exploratory"],
              ["BFI-10 traits", "Do traits moderate format effects?", "Exploratory; one trait at a time"],
              ["Demographics", "Describe sample; model only with a priori rationale", "Descriptive"],
            ]}
            striped
          />
        </Stack>
      </Grid>

      <CollapsibleSection title="Secondary behavioral outcomes and cautions" count={secondaryRows.length}>
        <Table
          headers={["Outcome", "Field / derivation", "Level", "Interpretation rule"]}
          rows={secondaryRows}
          striped
        />
      </CollapsibleSection>

      <Divider />

      <Stack gap={8}>
        <H2>EEG analysis direction</H2>
        <Text tone="secondary">
          The most defensible core is a within-participant, ad-locked comparison of the four ad conditions.
          A no-ad EEG contrast requires a validated matched reply-onset event, which current marker drift does
          not guarantee.
        </Text>
        <Table
          headers={["Analysis", "Time lock", "Measure", "Contrast", "Status"]}
          rows={eegCoreRows}
          striped
          stickyHeader
        />
      </Stack>

      <Grid columns="0.9fr 1.1fr" gap={20} align="start">
        <Stack gap={8}>
          <H2>EEG feasibility gates</H2>
          <Stack gap={10}>
            {[
              "Copy or mount the full-session XDF files from Drive.",
              "Create an explicit lab_subject ↔ XDF ↔ experiment_id mapping.",
              "Verify EEG and marker streams span the session and share the XDF clock.",
              "Deduplicate ad_displayed and use its first occurrence per condition.",
              "Freeze filtering, rereferencing, bad-channel, ICA, and epoch-rejection rules.",
              "Run the same preprocessing blind to condition labels before inferential modeling.",
            ].map((item, index) => (
              <div key={item}>
                <Row gap={10} align="start">
                  <Pill active={index < 3} size="sm">
                    {index + 1}
                  </Pill>
                  <Text>{item}</Text>
                </Row>
              </div>
            ))}
          </Stack>
        </Stack>

        <Stack gap={8}>
          <H2>Marker-specific consequences</H2>
          <Callout tone="warning">
            Subjects 5–7 lack turn_N_read, and its meaning changed during collection. This blocks a clean
            all-subject reading-onset analysis, but it does not automatically exclude those participants from
            ad_displayed-locked EEG if their full XDF and ad markers are valid.
          </Callout>
          <Text tone="secondary">
            ERP analysis is conditional because a visually precise onset must be demonstrated for both implicit
            and explicit formats. If implicit content appeared progressively during token streaming, sustained
            time-frequency analysis is more defensible than millisecond-scale ERP claims.
          </Text>
          <Text tone="secondary">
            Baseline should support normalization and quality control. FAA, engagement index, cognitive-load
            index, and classifier accuracy remain exploratory because their psychological interpretation is
            context-dependent and the participant count is small.
          </Text>
        </Stack>
      </Grid>

      <Stack gap={8}>
        <H2>Quality and exclusion plan</H2>
        <Table headers={["Layer", "Primary rule", "Sensitivity / rationale"]} rows={qualityRows} striped />
      </Stack>

      <Grid columns="1fr 1fr" gap={20} align="start">
        <Stack gap={8}>
          <H2>Preregistration sequence</H2>
          <Table
            headers={["Step", "Freeze before outcomes"]}
            rows={[
              ["1", "Canonical five conditions and analysis populations"],
              ["2", "Three primary outcome families and exact scoring"],
              ["3", "Contrast weights, covariates, and multiplicity correction"],
              ["4", "Behavioral and EEG exclusion thresholds"],
              ["5", "EEG ROIs, bands, windows, and onset-validation rule"],
              ["6", "Sensitivity analyses and confirmatory/exploratory labels"],
              ["7", "Code version and immutable analysis dataset manifest"],
            ]}
            striped
          />
        </Stack>

        <Stack gap={8}>
          <H2>Outputs the analysis pipeline should produce</H2>
          <Text tone="secondary">
            One participant table, one condition-level table, one turn-level table, one recall table, one EEG
            epoch manifest, and one exclusions ledger. Every result figure should be reproducible from those
            frozen intermediates.
          </Text>
          <Callout tone="success">
            The strongest final claim is likely convergence or divergence across measures: what users report,
            what they remember, how their interaction changes, and how ad-locked neural processing differs.
            The design should not imply that EEG directly reveals hidden persuasion.
          </Callout>
        </Stack>
      </Grid>

      <CollapsibleSection title="Evidence and source ledger" count={sourceRows.length}>
        <Table headers={["Source", "Use in this plan", "Location"]} rows={sourceRows} striped />
        <Text tone="tertiary" size="small">
          External methodological anchors:{" "}
          <Link href="https://doi.org/10.1145/3699682">Tang et al., IMWUT 2025</Link>
          {" · "}
          <Link href="https://arxiv.org/abs/2403.11022">Banchio et al., Ads in Conversations</Link>
        </Text>
      </CollapsibleSection>

      <Text tone="tertiary" size="small">
        Scope boundary: this is an analysis foundation, not a completed outcome analysis. No condition means
        or inferential results were inspected to formulate these goals.
      </Text>
    </Stack>
  );
}

export default App;

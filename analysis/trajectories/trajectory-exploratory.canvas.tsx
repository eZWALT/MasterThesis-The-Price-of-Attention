import {
  Button,
  Callout,
  Code,
  Divider,
  Grid,
  H1,
  H2,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useCanvasAction,
  useCanvasState,
} from "cursor/canvas";

type Section = "overview" | "redirection" | "responders" | "slicing" | "limits";

const SECTIONS: { id: Section; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "redirection", label: "Continuous redirection" },
  { id: "responders", label: "Responders & omnibus" },
  { id: "slicing", label: "The slice grid" },
  { id: "limits", label: "What this costs" },
];

const FIG =
  "/home/wtroi/MasterThesis-RAG-RecSys/analysis/trajectories/outputs/exploratory/figures";

function Open({ name, label }: { name: string; label: string }) {
  const dispatch = useCanvasAction();
  return (
    <Button
      variant="ghost"
      onClick={() => dispatch({ type: "openFile", path: `${FIG}/${name}.png` })}
    >
      {label}
    </Button>
  );
}

function Overview() {
  return (
    <Stack gap={16}>
      <Callout tone="warning" title="Exploratory. Never confirmatory.">
        Family A is locked in <Code>stages_2_4.md</Code> and is unchanged by
        this pass. Nothing here may be promoted into it. These are four new
        estimators on the same locked estimand, plus a priced version of the
        slicing that was asked for.
      </Callout>
      <Grid columns={4} gap={12}>
        <Stat value="−0.024" label="Continuous redirection (DiD)" />
        <Stat value="0.73" label="p, hidden-responder variance test" />
        <Stat value="0.44" label="p, transition-matrix omnibus" />
        <Stat value="0.79" label="Family-wise p, best of 81 cells" tone="warning" />
      </Grid>
      <Text>
        Four genuinely different ways of asking the question, each with a
        design-based null that permutes condition labels among a participant’s
        own five conversations. All four land in the same place.
      </Text>
      <Callout tone="info" title="Why this pass was warranted">
        Definition 6 is argmax on argmax: it crushes a 13-dimensional posterior
        into one bit and reports 9 of 108. A null on a lossy outcome is weak
        evidence. The continuous version recovers the discarded information and
        still finds nothing — which is a much stronger statement.
      </Callout>
      <Text tone="secondary">
        Script: <Code>run_exploratory.py</Code> · Report:{" "}
        <Code>outputs/exploratory/exploratory.md</Code> · N=54, bare utterance.
      </Text>
    </Stack>
  );
}

function Redirection() {
  return (
    <Stack gap={16}>
      <H2>Posterior mass on the advertised genre, turn 2 → turn 3</H2>
      <Text>
        Difference-in-differences: the change across the advertisement, minus
        the change on the <em>same</em> genre across the same turns in the same
        participant’s no-ad conversation. Person and baseline genre affinity
        both cancel.
      </Text>
      <Table
        headers={["Contrast", "Mean", "95% CI", "dz", "p"]}
        columnAlign={["left", "right", "right", "right", "right"]}
        striped
        rows={[
          ["Early pooled (DiD)", "−0.024", "[−0.088, +0.040]", "−0.10", "0.46"],
          ["Implicit early (DiD)", "−0.021", "[−0.119, +0.077]", "−0.06", "0.67"],
          ["Explicit early (DiD)", "−0.027", "[−0.093, +0.039]", "−0.11", "0.42"],
          ["Turn-3 mass, post only", "−0.028", "[−0.067, +0.012]", "−0.19", "0.16"],
          ["Best of turns 3–4", "−0.017", "[−0.052, +0.018]", "−0.13", "0.34"],
          ["PLACEBO late ads", "−0.028", "[−0.082, +0.026]", "−0.14", "0.30"],
        ]}
        rowTone={["info", undefined, undefined, undefined, undefined, "warning"]}
      />
      <Callout tone="success" title="The placebo is the point">
        Late advertisements appear after turn 4 and cannot have influenced turn
        3, yet their DiD is −0.028 — the same size as the early −0.024. The
        small negative is generic turn drift, not an advertisement.
      </Callout>
      <H2>How large a redirection is ruled out</H2>
      <Grid columns={3} gap={12}>
        <Stat value="0.134" label="Baseline mass on the ad genre" />
        <Stat value="+0.040" label="95% upper bound on the gain" />
        <Stat value="0.27" label="Smallest |dz| excluded" />
      </Grid>
      <Text>
        An advertisement would have to add more than 0.040 of posterior mass to
        the genre it advertises for this design to have caught it, against a
        0.134 baseline. That is a tighter bound than family A could state, and
        it is stated in the units Definition 6 is a threshold of.
      </Text>
      <H2>Does the genre ever arrive, even late</H2>
      <Text tone="secondary">
        Relaxing Definition 6’s “immediately next” to “turn 3 or turn 4”.
      </Text>
      <Table
        headers={["Contrast", "With ad", "Without", "Only ad", "Only control", "exact p"]}
        columnAlign={["left", "right", "right", "right", "right", "right"]}
        striped
        rows={[
          ["Early pooled", "24", "22", "15", "13", "0.85"],
          ["Implicit early", "13", "12", "9", "8", "1.00"],
          ["Explicit early", "11", "17", "7", "13", "0.26"],
          ["PLACEBO late", "32", "25", "16", "9", "0.23"],
        ]}
      />
      <Row gap={8} wrap>
        <Open name="sx_continuous_redirection" label="Open continuous redirection" />
      </Row>
    </Stack>
  );
}

function Responders() {
  return (
    <Stack gap={16}>
      <H2>Is the null hiding responders?</H2>
      <Text>
        A mean of zero is also what a population produces when half of it is
        pushed one way and half the other. That is a variance question, and it
        needs no subgroup at all.
      </Text>
      <Grid columns={3} gap={12}>
        <Stat value="0.469" label="Observed SD of person response" />
        <Stat value="0.493" label="Randomisation null, mean SD" />
        <Stat value="0.73" label="p (observed ≥ null)" />
      </Grid>
      <Callout tone="success" title="“Maybe it works for some people” is now retired">
        The spread of individual responses is exactly what shuffling condition
        labels inside a person already produces. There is no evidence of
        responders cancelling non-responders.
      </Callout>
      <Text tone="secondary">
        The same randomisation reproduces the confirmatory mean: +0.0463,
        two-sided p = 0.53, against the t-test’s 0.47. Family A survives a
        design-based null, not just a parametric one.
      </Text>
      <Divider />
      <H2>Omnibus on the whole transition matrix</H2>
      <Text>
        Family A tested one summary of the k=2 matrix. If advertisements
        rearranged <em>where</em> conversations go without changing{" "}
        <em>how often</em> they move, that test would miss it entirely.
      </Text>
      <Grid columns={4} gap={12}>
        <Stat value="0.537" label="Observed total variation" />
        <Stat value="0.526" label="Randomisation null mean" />
        <Stat value="65" label="Cells with any mass" />
        <Stat value="0.44" label="p" />
      </Grid>
      <Text tone="secondary">
        Observed separation is smaller than chance reassignment produces, which
        is what two samples from one distribution look like.
      </Text>
      <Row gap={8} wrap>
        <Open name="sx_heterogeneity" label="Open heterogeneity null" />
        <Open name="sx_omnibus" label="Open omnibus null" />
      </Row>
    </Stack>
  );
}

function Slicing() {
  return (
    <Stack gap={16}>
      <Callout tone="info" title="This is the part that was asked for">
        Every subgroup a reader might want — arm, task, session position, task
        genre, on both the advertisement and the control side — crossed with
        both crossing outcomes and all three treatment contrasts.
      </Callout>
      <Grid columns={4} gap={12}>
        <Stat value="81" label="Cells (slice × contrast on hard δ)" />
        <Stat value="0" label="Nominal hits below .05" />
        <Stat value="4.1" label="Expected by chance" />
        <Stat value="0.79" label="Family-wise p of the best cell" tone="warning" />
      </Grid>
      <Text>
        Zero cells clear .05, where chance predicts about four. The best
        cell anywhere in the grid has nominal p = 0.056, which is ordinary
        against a max-|t| randomisation null.
      </Text>
      <H2>The cells that would have been harvested</H2>
      <Table
        headers={["Slice", "Contrast", "Outcome", "n", "Nominal p", "Family-wise p"]}
        columnAlign={["left", "left", "left", "right", "right", "right"]}
        striped
        rows={[
          ["control session position = 1", "implicit early", "δ", "16", "0.056", "0.79"],
          ["control session position = 1", "early pooled", "δ", "16", "0.104", "1.00"],
          ["arm = lab", "explicit early", "δ", "18", "0.187", "1.00"],
          ["arm = lab", "early pooled", "δ", "18", "0.205", "1.00"],
        ]}
        rowTone={["warning", undefined, undefined, undefined]}
      />
      <Callout tone="success" title="Use this table defensively">
        If a subgroup claim is ever proposed from this dataset, this is the
        reason it cannot be made. <Code>laptop_budget</Code> and{" "}
        <Code>arm = lab</Code> are the two that would have been harvested.
        Both die here.
      </Callout>
      <Row gap={8} wrap>
        <Open name="sx_slice_grid" label="Open slice grid" />
      </Row>
    </Stack>
  );
}

function Limits() {
  return (
    <Stack gap={16}>
      <Callout tone="warning" title="Definition 6 is weak on this corpus">
        The advertised genre is 58% <Code>general_guidance_and_info</Code> (126
        of 216) at mean classifier confidence 0.40. So the hard redirection test
        is largely asking whether the modal genre lands on the modal genre.
        This is a limitation to disclose in §7.5, not a result.
      </Callout>
      <H2>Contextual sensitivity</H2>
      <Table
        headers={["Contrast", "Mean", "95% CI", "p", "Baseline mass"]}
        columnAlign={["left", "right", "right", "right", "right"]}
        striped
        rows={[
          ["Contextual early pooled (DiD)", "−0.006", "[−0.022, +0.011]", "0.49", "0.271"],
          ["Contextual PLACEBO late", "−0.015", "[−0.030, +0.001]", "0.057", "0.261"],
        ]}
        rowTone={[undefined, "warning"]}
      />
      <Callout tone="info" title="Read the placebo row carefully">
        Under contextual labels the <em>late</em> condition — whose
        advertisement had not yet appeared when the measured turn was written —
        comes closer to significance (p = 0.057) than the condition that was
        actually exposed (p = 0.49). Small negative drifts of this size are what
        these turns do on their own.
      </Callout>
      <Divider />
      <H2>Bug found and fixed this pass</H2>
      <Text>
        <Code>gee_crossing()</Code> imported <Code>smf</Code> and then called{" "}
        <Code>sm</Code>, so the generated stages 2–4 report contained{" "}
        <Code>model failed: name &apos;sm&apos; is not defined</Code> while the
        context note quoted OR 1.31. The number was right; the report was
        broken. Two paper figures and <Code>s24_paper_pack.pdf</Code> were also
        listed but absent. All now on disk.
      </Text>
      <Callout tone="neutral" title="Where this leaves the arm">
        Four estimators, a design-based null, a working placebo and a priced
        slice grid all agree. The remaining routes to a positive result need a
        different labelling scheme or a different experiment, not another test.
        Stage 5 stays blocked. Writing is yours.
      </Callout>
    </Stack>
  );
}

export default function TrajectoryExploratory() {
  const [section, setSection] = useCanvasState<Section>("section", "overview");
  return (
    <Stack gap={20}>
      <Stack gap={8}>
        <H1>Trajectories · exploratory pass</H1>
        <Text tone="secondary">
          New estimators, not new subgroups. The slicing was run and priced
          rather than mined. Bare utterance primary, N=54.
        </Text>
      </Stack>
      <Row gap={8} wrap>
        {SECTIONS.map((item) => (
          <span key={item.id}>
            <Pill active={section === item.id} onClick={() => setSection(item.id)}>
              {item.label}
            </Pill>
          </span>
        ))}
      </Row>
      <Divider />
      {section === "overview" ? <Overview /> : null}
      {section === "redirection" ? <Redirection /> : null}
      {section === "responders" ? <Responders /> : null}
      {section === "slicing" ? <Slicing /> : null}
      {section === "limits" ? <Limits /> : null}
    </Stack>
  );
}

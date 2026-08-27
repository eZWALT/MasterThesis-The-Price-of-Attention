import {
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
  useCanvasState,
} from "cursor/canvas";

type Section = "overview" | "pvalues" | "stickiness";

const SECTIONS: { id: Section; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "pvalues", label: "Every p-value" },
  { id: "stickiness", label: "What the window does" },
];

function Overview() {
  return (
    <Stack gap={16}>
      <Callout tone="warning" title="Sensitivity. Not family A.">
        Six ways to feed ThradBERT. Same crossing estimand as stages 2–4.
        Hard labels only. Holm-across is the six early-pooled tests — the
        number you would harvest.
      </Callout>
      <Grid columns={4} gap={12}>
        <Stat value="0" label="Recipes with p < .05" />
        <Stat value="0.096" label="Smallest unadjusted p (wrong sign)" />
        <Stat value="0.58" label="Holm-across, that same cell" />
        <Stat value="270/270" label="Task prompts recovered" />
      </Grid>
      <Callout tone="info" title="The pain point is real. It is not the null.">
        The live window (task + last 3) is almost frozen: 70% of conversations
        never change genre. Strip the task and movement more than doubles.
        The advertisement contrast stays null. The liveliest window that is
        not bare — previous message only — is the closest to .05, and ads
        shift <em>less</em> there, not more.
      </Callout>
      <Text tone="secondary">
        Script: <Code>run_contextual_sweep.py</Code> · Report:{" "}
        <Code>outputs/contextual_sweep/contextual_sweep.md</Code>
      </Text>
    </Stack>
  );
}

function Pvalues() {
  return (
    <Stack gap={16}>
      <H2>Early pooled − no-ad, hard δ</H2>
      <Table
        headers={["Recipe", "What it sees", "Mean δ", "Unadj. p", "Holm across"]}
        columnAlign={["left", "left", "right", "right", "right"]}
        striped
        rows={[
          ["bare", "current message", "+0.046", "0.47", "1.00"],
          ["deployed", "task + last 3 + current", "−0.019", "0.76", "1.00"],
          ["no_task", "last 3 + current", "+0.009", "0.90", "1.00"],
          ["prev_only", "previous + current", "−0.139", "0.096", "0.58"],
          ["task_only", "task + current", "−0.019", "0.76", "1.00"],
          ["opening", "first message + current", "−0.056", "0.45", "1.00"],
        ]}
        rowTone={[undefined, undefined, undefined, "warning", undefined, undefined]}
      />
      <H2>McNemar, implicit early − no-ad</H2>
      <Table
        headers={["Recipe", "Only ad", "Only no-ad", "exact p"]}
        columnAlign={["left", "right", "right", "right"]}
        striped
        rows={[
          ["bare", "11", "6", "0.33"],
          ["deployed", "5", "6", "1.00"],
          ["no_task", "11", "8", "0.65"],
          ["prev_only", "10", "17", "0.25"],
          ["task_only", "6", "9", "0.61"],
          ["opening", "12", "13", "1.00"],
        ]}
      />
      <H2>Definition 6, δ-tilde</H2>
      <Table
        headers={["Recipe", "Observed", "Chance", "p"]}
        columnAlign={["left", "right", "right", "right"]}
        striped
        rows={[
          ["bare", "9", "10.5", "0.79"],
          ["deployed", "2", "3.7", "0.97"],
          ["no_task", "7", "8.7", "0.88"],
          ["prev_only", "9", "10.5", "0.80"],
          ["task_only", "3", "4.2", "0.88"],
          ["opening", "10", "11.7", "0.84"],
        ]}
      />
      <Text tone="secondary">
        Closest cell is prev_only, unadjusted p = 0.096, ads reduce shifts.
        That is not a finding.
      </Text>
    </Stack>
  );
}

function Stickiness() {
  return (
    <Stack gap={16}>
      <H2>The task prompt is the glue</H2>
      <Table
        headers={["Recipe", "Genres used", "Mean N_shift / 3", "Fully sticky"]}
        columnAlign={["left", "right", "right", "right"]}
        striped
        rows={[
          ["bare", "13", "2.45", "3%"],
          ["prev_only", "13", "1.59", "10%"],
          ["opening", "12", "1.28", "37%"],
          ["no_task", "12", "0.94", "38%"],
          ["task_only", "5", "0.50", "68%"],
          ["deployed", "7", "0.40", "70%"],
        ]}
        rowTone={[undefined, undefined, undefined, undefined, "warning", "warning"]}
      />
      <Callout tone="success" title="What this changes for the write-up">
        Disclose that the deployed window is sticky because of the task
        prompt. That is a limitation of the live system, not a rescue of
        the advertisement null. Primary stays bare utterance.
      </Callout>
    </Stack>
  );
}

export default function ContextualSweep() {
  const [section, setSection] = useCanvasState<Section>("section", "overview");
  return (
    <Stack gap={20}>
      <Stack gap={8}>
        <H1>Trajectories · contextual sweep</H1>
        <Text tone="secondary">
          Other ways to give the classifier context. Looking for a p-value.
          There isn’t one.
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
      {section === "pvalues" ? <Pvalues /> : null}
      {section === "stickiness" ? <Stickiness /> : null}
    </Stack>
  );
}

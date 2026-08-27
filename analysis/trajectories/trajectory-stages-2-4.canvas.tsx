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

type Section = "overview" | "crossing" | "redirection" | "moderation" | "cut";

const SECTIONS: { id: Section; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "crossing", label: "Stage 2" },
  { id: "redirection", label: "Stage 3" },
  { id: "moderation", label: "Stage 4" },
  { id: "cut", label: "Figure cut" },
];

const FIG =
  "/home/wtroi/MasterThesis-RAG-RecSys/analysis/trajectories/outputs/stages_2_4/figures";

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
      <Callout tone="info" title="Family A, locked. Hard labels only.">
        Crossing hard δ; implicit − explicit on hard δ; δ-tilde permutation.
        Holm within the hard-δ family. Destinations descriptive. Timing is
        a negative control. Contextual is sensitivity. Stage 5 blocked.
        Jensen–Shannon is out.
      </Callout>
      <Grid columns={4} gap={12}>
        <Stat value="+0.046" label="Crossing δ, early − no-ad" />
        <Stat value="0.94" label="Holm p (hard δ)" />
        <Stat value="1.31" label="Like-for-like GEE OR (p=.51)" />
        <Stat value="9 / 10.5" label="δ-tilde vs chance" />
      </Grid>
      <Callout tone="neutral" title="The 25/108 footnote">
        If someone is already in the ad’s genre at turn 2, staying there is
        not a shift, so Definition 6 cannot fire. Those 25 count as zeros.
        Dropping them: 9/83 = 0.108 instead of 9/108 = 0.083. Still at chance.
      </Callout>
      <Callout tone="warning" title="Retired number">
        The first-pass GEE OR 0.99 mixed all three no-ad transitions with the
        k=2 crossing rows. Do not quote it. Like-for-like k=2 is OR 1.31,
        p = .51.
      </Callout>
      <Text tone="secondary">
        Precision: |dz| &gt; 0.27 is excluded. Depth moves (guidance dz=−1.00).
        Script: <Code>run_stages_2_4.py</Code>
      </Text>
    </Stack>
  );
}

function Crossing() {
  return (
    <Stack gap={16}>
      <H2>Crossing transition 2→3, N=54</H2>
      <Table
        headers={["Contrast", "Mean δ", "95% CI", "dz", "Holm p"]}
        columnAlign={["left", "right", "right", "right", "right"]}
        striped
        rows={[
          ["Early pooled − no ad", "+0.046", "[−0.082, 0.174]", "0.10", "0.94"],
          ["Implicit early − no ad", "+0.093", "[−0.060, 0.245]", "0.17", "0.91"],
          ["Explicit early − no ad", "0.000", "[−0.150, 0.150]", "0.00", "1.00"],
          ["Implicit − explicit", "+0.093", "[−0.069, 0.254]", "0.16", "0.91"],
        ]}
        rowTone={["info", undefined, undefined, "warning"]}
      />
      <H2>Exact McNemar</H2>
      <Table
        headers={["Contrast", "Treated shift", "Control shift", "Only T", "Only C", "exact p"]}
        columnAlign={["left", "right", "right", "right", "right", "right"]}
        striped
        rows={[
          ["Implicit early − no ad", "47", "42", "11", "6", "0.33"],
          ["Explicit early − no ad", "42", "42", "8", "8", "1.00"],
          ["Implicit − explicit", "47", "42", "12", "7", "0.36"],
        ]}
      />
      <Row gap={8} wrap>
        <Open name="s24_crossing_forest" label="Open forest" />
        <Open name="s24_depth_versus_ad" label="Open depth vs ad" />
        <Open name="s24_mcnemar" label="Open McNemar" />
        <Open name="s24_person_pairs" label="Open person pairs" />
        <Open name="s24_destinations" label="Open destinations" />
        <Open name="s24_adjacent" label="Open adjacent" />
      </Row>
    </Stack>
  );
}

function Redirection() {
  return (
    <Stack gap={16}>
      <H2>Definition 6 on 108 early advertisements</H2>
      <Grid columns={3} gap={12}>
        <Stat value="19 / 108" label="Same genre (no shift)" />
        <Stat value="80 / 108" label="Unrelated shift" />
        <Stat value="9 / 108" label="Ad-aligned shift (δ-tilde)" tone="warning" />
      </Grid>
      <Text>
        q = P(aligned | shifted) = 9/89 = 0.101. Permutation chance is 10.46,
        p = 0.80. Alignment is slightly below coincidence and concentrated in
        guidance, which both the ads and the utterances already prefer.
      </Text>
      <Table
        headers={["Ad type", "n", "Same", "Unrelated", "Aligned", "Already in genre"]}
        columnAlign={["left", "right", "right", "right", "right", "right"]}
        striped
        rows={[
          ["Implicit early", "54", "7", "43", "4", "14"],
          ["Explicit early", "54", "12", "37", "5", "11"],
        ]}
      />
      <Row gap={8} wrap>
        <Open name="s24_redirection" label="Open stacked" />
        <Open name="s24_permutation" label="Open permutation" />
      </Row>
    </Stack>
  );
}

function Moderation() {
  return (
    <Stack gap={16}>
      <Callout tone="warning" title="Timing is not a treatment moderator">
        A turn-4 ad has no following utterance. Late vs no-ad is a negative
        control. Type (implicit vs explicit) is tested on the crossing
        estimand: +0.093, Holm p = 0.91.
      </Callout>
      <Table
        headers={["Contrast", "Mean N_shift", "95% CI", "dz", "Holm p"]}
        columnAlign={["left", "right", "right", "right", "right"]}
        striped
        rows={[
          ["Late pooled − no ad", "−0.074", "[−0.361, 0.213]", "−0.07", "1.00"],
          ["Implicit late − no ad", "−0.019", "[−0.348, 0.310]", "−0.02", "1.00"],
          ["Explicit late − no ad", "−0.130", "[−0.444, 0.184]", "−0.11", "1.00"],
        ]}
      />
      <H2>Contextual sensitivity</H2>
      <Text tone="secondary">
        Crossing hard δ, early pooled − no-ad: −0.018, Holm p = 1.00. Same
        null, closer to zero, as expected from a sticky chain.
      </Text>
      <Open name="s24_negative_control" label="Open negative control" />
    </Stack>
  );
}

function Cut() {
  return (
    <Stack gap={16}>
      <Callout tone="success" title="Decided with the run">
        Paper: forest, redirection stacked, permutation histogram. Tables
        for the numbers. Appendix: McNemar boards, destinations, late
        control, person pairs.
      </Callout>
      <Table
        headers={["Slot", "Figure", "Insight"]}
        rows={[
          ["Paper", "s24_crossing_forest", "Family A. No interval excludes 0."],
          ["Paper", "s24_depth_versus_ad", "Depth moves; ads do not. Pipeline check."],
          ["Paper", "s24_redirection", "8% aligned, 74% unrelated, 18% stay."],
          ["Paper", "s24_permutation", "9 vs 10.5 chance, p = 0.80."],
          ["Appendix", "s24_mcnemar", "Discordant pairs behind the exact test."],
          ["Appendix", "s24_destinations", "To what. purchasable is 4/89."],
          ["Appendix", "s24_negative_control", "Late is a control, not a level."],
          ["Appendix", "s24_person_pairs", "Most people already shift on 2→3."],
          ["Appendix", "s24_adjacent", "Turn-3 words and latency, label-free."],
        ]}
        rowTone={["info", "info", "info", "neutral", "neutral", "neutral", "neutral"]}
      />
    </Stack>
  );
}

export default function TrajectoryStages24() {
  const [section, setSection] = useCanvasState<Section>("section", "overview");
  return (
    <Stack gap={20}>
      <Stack gap={8}>
        <H1>Stages 2–4 · Advertisements and genre</H1>
        <Text tone="secondary">
          Crossing estimand, Definition 6, type yes / timing no. Bare
          utterance primary. Hard labels only. You write; these are the numbers.
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
      {section === "crossing" ? <Crossing /> : null}
      {section === "redirection" ? <Redirection /> : null}
      {section === "moderation" ? <Moderation /> : null}
      {section === "cut" ? <Cut /> : null}
    </Stack>
  );
}

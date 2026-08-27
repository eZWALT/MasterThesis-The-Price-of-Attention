import {
  BarChart,
  Button,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Code,
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
  useCanvasAction,
  useCanvasState,
} from "cursor/canvas";

type Section =
  | "overview"
  | "genres"
  | "measures"
  | "transitions"
  | "validity"
  | "appendix"
  | "cut";

const SECTIONS: { id: Section; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "genres", label: "Genres" },
  { id: "measures", label: "Measures" },
  { id: "transitions", label: "Transitions" },
  { id: "validity", label: "Validity" },
  { id: "appendix", label: "Appendix" },
  { id: "cut", label: "Figure cut" },
];

const FIG = "/home/wtroi/MasterThesis-RAG-RecSys/analysis/trajectories/outputs/eda/figures";
const CONDITIONS = ["No ad", "Impl. early", "Expl. early", "Impl. late", "Expl. late"];
const TURNS = ["Turn 1", "Turn 2", "Turn 3", "Turn 4"];

function OpenFigure({ name, label }: { name: string; label: string }) {
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
    <Stack gap={18}>
      <Callout tone="warning" title="Descriptive only">
        No advertisement contrast is tested here. The five conditions look
        the same because they are; the estimand for stage 2 is the crossing
        transition, not these conversation-level aggregates.
      </Callout>
      <Callout tone="info" title="Ceiling, not richness">
        Diversity is bounded by T=4 turns, not by the 13 classes. Bare
        trajectories visit 3.10 of a possible 4 genres (78% of ceiling). The
        21 Aug note that said “3.10 of 13” is wrong and has been corrected.
      </Callout>

      <Grid columns={4} gap={12}>
        <Stat value="54" label="Participants (18 lab, 36 crowd)" />
        <Stat value="270" label="Conversations (5 each)" />
        <Stat value="1,080" label="User utterances" />
        <Stat value="810" label="Transitions" />
      </Grid>
      <Grid columns={4} gap={12}>
        <Stat value="2.45 / 3" label="Mean N_shift (82% of ceiling)" tone="warning" />
        <Stat value="3.10 / 4" label="Mean diversity (78% of ceiling)" tone="warning" />
        <Stat value="1.05 / 1.39" label="Mean entropy, nats (76%)" tone="warning" />
        <Stat value="97.4%" label="Conversations with ≥1 shift" />
      </Grid>

      <H2>Where the variance sits</H2>
      <Text tone="secondary">
        Kruskal–Wallis on N_shift. These ask which design factor a measure
        varies with at all. They are not advertisement tests. Participant ICC
        is 0.07, so people do not have stable trajectory styles either.
      </Text>
      <Table
        headers={["Factor", "Levels", "H", "p", "η² / ICC"]}
        columnAlign={["left", "right", "right", "right", "right"]}
        striped
        rows={[
          ["Condition", "5", "2.89", ".58", "0.009"],
          ["Task", "5", "4.61", ".33", "0.021"],
          ["Arm", "2", "0.04", ".85", "0.003"],
          ["Session position", "4", "2.25", ".52", "0.009"],
          ["Participant (ICC)", "54", "—", "—", "0.067"],
        ]}
      />

      <H2>Six observed trajectories</H2>
      <Text tone="secondary" size="small">
        Real conversations under the bare-utterance labelling. Filled cells
        mark a genre shift. The orange “ad” marker is the insertion point; a
        turn-4 ad has no following utterance.
      </Text>
      <Table
        headers={["Caption", "Turn 1", "Turn 2", "Ad", "Turn 3", "Turn 4"]}
        rows={[
          ["No ad, stays put", "guidance", "guidance", "—", "guidance", "guidance"],
          ["No ad, moves every turn", "personal writing", "guidance", "—", "academic", "other"],
          ["Implicit early", "relationships", "relationships", "after 2", "academic", "academic"],
          ["Explicit early", "guidance", "guidance", "after 2", "obscene/illegal", "relationships"],
          ["Implicit late", "creative writing", "academic", "after 4", "guidance", "guidance"],
          ["Explicit late", "guidance", "academic", "after 4", "relationships", "guidance"],
        ]}
        rowTone={[
          "neutral",
          "info",
          "warning",
          "warning",
          undefined,
          undefined,
        ]}
      />
      <Row gap={8} wrap>
        <OpenFigure name="eda_example_trajectories" label="Open example figure" />
        <OpenFigure name="eda_measures_by_condition" label="Open measures figure" />
      </Row>
    </Stack>
  );
}

function Genres() {
  return (
    <Stack gap={16}>
      <H2>Genre distribution (bare utterance)</H2>
      <Text tone="secondary">
        1,080 utterances. Orange fallback classes in the paper figure are
        other and obscene/illegal. purchasable_products is 19 of 1,080 despite
        every task being a shopping scenario.
      </Text>
      <BarChart
        horizontal
        height={340}
        categories={[
          "guidance",
          "relationships",
          "academic",
          "obscene/illegal",
          "personal writing",
          "other",
          "creative writing",
          "ideation",
          "greetings",
          "writing",
          "media",
          "purchasable",
          "programming",
        ]}
        series={[
          {
            name: "Utterances",
            data: [350, 193, 110, 86, 72, 71, 43, 39, 35, 34, 27, 19, 1],
          },
        ]}
        showValues
      />
      <Text tone="tertiary" size="small">
        Source: utterances.csv, genre_source = utterance · n = 1,080
      </Text>
      <Table
        headers={["Genre", "n", "Share", "People", "Top p", "Median words"]}
        columnAlign={["left", "right", "right", "right", "right", "right"]}
        striped
        stickyHeader
        rows={[
          ["guidance", "350", "32.4%", "54", "0.43", "21"],
          ["relationships", "193", "17.9%", "53", "0.45", "13"],
          ["academic", "110", "10.2%", "45", "0.45", "26"],
          ["obscene/illegal", "86", "8.0%", "42", "0.41", "11"],
          ["personal writing", "72", "6.7%", "37", "0.44", "9"],
          ["other", "71", "6.6%", "39", "0.37", "11"],
          ["creative writing", "43", "4.0%", "31", "0.43", "23"],
          ["ideation", "39", "3.6%", "26", "0.44", "24"],
          ["greetings", "35", "3.2%", "24", "0.46", "9"],
          ["writing", "34", "3.1%", "25", "0.38", "16"],
          ["media", "27", "2.5%", "19", "0.37", "19"],
          ["purchasable", "19", "1.8%", "15", "0.36", "13"],
          ["programming", "1", "0.1%", "1", "0.36", "4"],
        ]}
        rowTone={[
          undefined,
          undefined,
          undefined,
          "warning",
          undefined,
          "warning",
        ]}
      />
      <OpenFigure name="eda_genre_distribution" label="Open paper figure" />
    </Stack>
  );
}

function Measures() {
  return (
    <Stack gap={18}>
      <H2>Every measure is discrete and flat</H2>
      <Text tone="secondary">
        With T=4, N_shift takes four values, diversity four, persistence four,
        and entropy only the five achievable partitions of four turns. Orange
        numerals in the paper figure are condition means. n = 54 conversations
        per condition.
      </Text>
      <Grid columns={2} gap={16}>
        <Stack gap={6}>
          <H3>N_shift (max 3)</H3>
          <BarChart
            categories={CONDITIONS}
            stacked
            normalized
            height={220}
            valueSuffix="%"
            series={[
              { name: "0", data: [1.9, 1.9, 1.9, 5.6, 1.9] },
              { name: "1", data: [11.1, 3.7, 7.4, 3.7, 13.0] },
              { name: "2", data: [24.1, 31.5, 38.9, 29.6, 33.3] },
              { name: "3", data: [63.0, 63.0, 51.9, 61.1, 51.9] },
            ]}
          />
          <Text tone="tertiary" size="small">
            Means: 2.48, 2.56, 2.41, 2.46, 2.35
          </Text>
        </Stack>
        <Stack gap={6}>
          <H3>Diversity D (max 4)</H3>
          <BarChart
            categories={CONDITIONS}
            stacked
            normalized
            height={220}
            valueSuffix="%"
            series={[
              { name: "1", data: [1.9, 1.9, 1.9, 5.6, 1.9] },
              { name: "2", data: [16.7, 11.1, 16.7, 14.8, 13.0] },
              { name: "3", data: [50.0, 55.6, 48.1, 53.7, 57.4] },
              { name: "4", data: [31.5, 31.5, 33.3, 25.9, 27.8] },
            ]}
          />
          <Text tone="tertiary" size="small">
            Means: 3.11, 3.17, 3.13, 3.00, 3.11
          </Text>
        </Stack>
        <Stack gap={6}>
          <H3>Entropy H, nats (max 1.386)</H3>
          <BarChart
            categories={CONDITIONS}
            stacked
            normalized
            height={220}
            valueSuffix="%"
            series={[
              { name: "0", data: [1.9, 1.9, 1.9, 5.6, 1.9] },
              { name: "0.562", data: [13.0, 5.6, 11.1, 9.3, 11.1] },
              { name: "0.693", data: [3.7, 5.6, 5.6, 5.6, 1.9] },
              { name: "1.04", data: [50.0, 55.6, 48.1, 53.7, 57.4] },
              { name: "1.386", data: [31.5, 31.5, 33.3, 25.9, 27.8] },
            ]}
          />
          <Text tone="tertiary" size="small">
            Means: 1.06, 1.08, 1.06, 1.01, 1.06
          </Text>
        </Stack>
        <Stack gap={6}>
          <H3>Max persistence R (max 4)</H3>
          <BarChart
            categories={CONDITIONS}
            stacked
            normalized
            height={220}
            valueSuffix="%"
            series={[
              { name: "1", data: [63.0, 63.0, 51.9, 61.1, 51.9] },
              { name: "2", data: [24.1, 33.3, 40.7, 29.6, 35.2] },
              { name: "3", data: [11.1, 1.9, 5.6, 3.7, 11.1] },
              { name: "4", data: [1.9, 1.9, 1.9, 5.6, 1.9] },
            ]}
          />
          <Text tone="tertiary" size="small">
            Means: 1.52, 1.43, 1.57, 1.54, 1.63
          </Text>
        </Stack>
      </Grid>

      <H3>Pooled descriptives (n = 270 conversations)</H3>
      <Table
        headers={["Measure", "Ceiling", "Mean", "SD", "95% CI", "Median [IQR]"]}
        columnAlign={["left", "right", "right", "right", "right", "right"]}
        striped
        rows={[
          ["N_shift", "3", "2.45", "0.75", "2.36–2.54", "3 [2, 3]"],
          ["Diversity D", "4", "3.10", "0.73", "3.02–3.19", "3 [3, 4]"],
          ["Entropy H (nats)", "1.386", "1.05", "0.30", "1.02–1.09", "1.04 [1.04, 1.39]"],
          ["Max persistence R", "4", "1.54", "0.74", "1.45–1.63", "1 [1, 2]"],
        ]}
      />

      <H2>Runs and shifts, all conditions pooled</H2>
      <Grid columns={2} gap={16}>
        <Stack gap={6}>
          <H3>Genre persistence R(g)</H3>
          <BarChart
            categories={["1 turn", "2", "3", "4"]}
            series={[{ name: "Share of maximal runs", data: [87.6, 9.8, 1.9, 0.8] }]}
            valueSuffix="%"
            height={200}
            showValues
          />
          <Text tone="tertiary" size="small">
            932 maximal runs · 87.6% last a single turn
          </Text>
        </Stack>
        <Stack gap={6}>
          <H3>Shifts per conversation</H3>
          <BarChart
            categories={["0", "1", "2", "3"]}
            series={[{ name: "Share of conversations", data: [2.6, 7.8, 31.5, 58.1] }]}
            valueSuffix="%"
            height={200}
            showValues
          />
          <Text tone="tertiary" size="small">
            270 conversations · 58.1% shift on all three transitions
          </Text>
        </Stack>
      </Grid>
      <Row gap={8} wrap>
        <OpenFigure name="eda_measures_by_condition" label="Open measures figure" />
        <OpenFigure name="eda_persistence" label="Open persistence figure" />
      </Row>
    </Stack>
  );
}

function Transitions() {
  return (
    <Stack gap={16}>
      <Grid columns={3} gap={12}>
        <Stat value="0.183" label="Self-transition mass (diagonal)" />
        <Stat value="0.817" label="Shift rate" />
        <Stat value="120 / 169" label="Distinct genre pairs observed" />
      </Grid>
      <Text tone="secondary">
        Modal destination is guidance (27.3%). Top edges: guidance→guidance
        82, guidance→relationships 56, relationships→guidance 36. Rows with
        few outgoing transitions are unstable; programming is reached once,
        at turn 4, so it has no outgoing row.
      </Text>
      <H2>Genre mix by turn</H2>
      <LineChart
        categories={TURNS}
        height={240}
        yMax={0.55}
        showValues
        series={[
          { name: "Guidance", data: [0.478, 0.322, 0.285, 0.211] },
          { name: "Relationships", data: [0.152, 0.189, 0.196, 0.178] },
          { name: "Fallback classes", data: [0.041, 0.152, 0.189, 0.200], tone: "warning" },
          { name: "Academic", data: [0.130, 0.107, 0.093, 0.078] },
          { name: "Personal writing", data: [0.048, 0.052, 0.048, 0.119] },
        ]}
      />
      <Text tone="tertiary" size="small">
        Share of 270 utterances per turn · fallback = other + obscene/illegal
      </Text>
      <Callout tone="neutral" title="The paper heatmap is the money plot">
        The canvas cannot render a 13×13 annotated matrix cleanly. Open the
        PDF/PNG; row counts sit on the tick labels so the thin rows are not
        read cellwise.
      </Callout>
      <Row gap={8} wrap>
        <OpenFigure name="eda_transition_heatmap" label="Open heatmap" />
        <OpenFigure name="eda_turn_profile" label="Open turn profile" />
      </Row>
    </Stack>
  );
}

function Validity() {
  return (
    <Stack gap={16}>
      <Callout tone="warning" title="A property of the instrument">
        This subsection qualifies everything above. Later messages are
        elliptical, and a single-utterance classifier has less to work with.
        Confidence does not decline, so the drift is not the model degrading.
      </Callout>
      <Grid columns={2} gap={16}>
        <Stack gap={6}>
          <H3>Messages get shorter</H3>
          <BarChart
            categories={TURNS}
            series={[{ name: "Median words", data: [40, 14, 13, 10] }]}
            height={200}
            showValues
          />
          <Text tone="tertiary" size="small">
            IQR turn 1: 22–58 · turn 4: 6–17
          </Text>
        </Stack>
        <Stack gap={6}>
          <H3>Fallback labels grow; confidence is flat</H3>
          <LineChart
            categories={TURNS}
            height={200}
            yMax={0.5}
            showValues
            referenceLines={[{ value: 0.077, label: "Chance 1/13" }]}
            series={[
              { name: "Fallback share", data: [0.041, 0.152, 0.189, 0.200], tone: "warning" },
              { name: "Mean top posterior", data: [0.427, 0.425, 0.425, 0.430] },
            ]}
          />
        </Stack>
      </Grid>
      <Table
        headers={[
          "Turn",
          "n",
          "Median words",
          "IQR",
          "Fallback share",
          "Mean top p",
          "Distinct genres",
        ]}
        columnAlign={["right", "right", "right", "right", "right", "right", "right"]}
        striped
        rows={[
          ["1", "270", "40", "22–58", "4.1%", "0.427", "12"],
          ["2", "270", "14", "8–24", "15.2%", "0.425", "12"],
          ["3", "270", "13", "7–20", "18.9%", "0.425", "12"],
          ["4", "270", "10", "6–17", "20.0%", "0.430", "13"],
        ]}
      />
      <H3>Logistic models for a fallback label (clustered by participant)</H3>
      <Table
        headers={["Model", "Term", "β", "SE", "p"]}
        columnAlign={["left", "left", "right", "right", "right"]}
        striped
        rows={[
          ["junk ~ turn", "turn", "0.43", "0.08", "< .001"],
          ["junk ~ turn + log(words)", "turn", "0.34", "0.09", "< .001"],
          ["junk ~ turn + log(words)", "log(words)", "−0.29", "0.09", "< .001"],
        ]}
      />
      <Text tone="secondary">
        Length explains part of the drift: the turn coefficient shrinks from
        0.43 to 0.34 once words are in. It does not explain all of it. Mean
        top posterior stays at 0.43. Both halves belong in the write-up.
      </Text>
      <OpenFigure name="eda_label_validity" label="Open validity figure" />
    </Stack>
  );
}

function Appendix() {
  return (
    <Stack gap={16}>
      <Callout tone="neutral" title="Contextual lives only in the appendix">
        Same 1,080 messages and 810 transitions. Contextual reproduces the
        runtime labels 1,080/1,080. Bare agrees 32.5% of the time. They are
        different dynamical systems.
      </Callout>
      <Grid columns={2} gap={16}>
        <Stack gap={8}>
          <H3>Bare (primary)</H3>
          <Stat value="13 / 13" label="Classes used" />
          <Stat value="0.18" label="Self-transition mass" />
          <Stat value="2.45" label="Mean N_shift of 3" />
          <Stat value="3.10" label="Mean diversity of 4" />
        </Stack>
        <Stack gap={8}>
          <H3>Contextual (deployed)</H3>
          <Stat value="7 / 13" label="Classes used" />
          <Stat value="0.87" label="Self-transition mass" />
          <Stat value="0.40" label="Mean N_shift of 3" />
          <Stat value="1.33" label="Mean diversity of 4" />
        </Stack>
      </Grid>
      <H3>Contextual genre shares</H3>
      <BarChart
        horizontal
        height={220}
        categories={[
          "guidance",
          "academic",
          "relationships",
          "creative writing",
          "ideation",
          "writing",
          "personal writing",
        ]}
        series={[
          {
            name: "Utterances",
            data: [755, 244, 69, 8, 2, 1, 1],
            tone: "warning",
          },
        ]}
        showValues
      />
      <Text tone="tertiary" size="small">
        Guidance 69.9% · academic 22.6% · relationships 6.4% · the rest 1.1%
      </Text>
      <OpenFigure name="eda_appendix_contextual" label="Open appendix figure" />
    </Stack>
  );
}

function FigureCut() {
  return (
    <Stack gap={16}>
      <Callout tone="success" title="Decided 23 Aug">
        Paper: three figures (measures, heatmap, validity) plus two small
        tables. If stage 2 gets a crossing forest, demote the measures board
        so §6.4 does not carry two flat pictures. Nothing staged to Overleaf
        yet.
      </Callout>
      <Table
        headers={["Slot", "Figure", "Insight"]}
        rows={[
          [
            "Paper §6.4",
            "eda_measures_by_condition",
            "Aggregates do not differ by condition. Caption: not a test.",
          ],
          [
            "Paper §6.4",
            "eda_transition_heatmap",
            "Leaky chain, guidance attractor, thin rows unstable.",
          ],
          [
            "Paper or Methods",
            "eda_label_validity",
            "Messages shorten, fallback 4%→20%, confidence flat.",
          ],
          [
            "Paper table",
            "T3 pooled + T4",
            "Ceilings, and variance sits nowhere.",
          ],
          [
            "Appendix",
            "eda_appendix_contextual",
            "Two readings are different dynamical systems.",
          ],
          [
            "Appendix",
            "eda_example_trajectories",
            "Six real T=4 paths with the ad rule.",
          ],
          [
            "Appendix",
            "eda_turn_profile",
            "Guidance 0.48→0.21. Quote the numbers in the text.",
          ],
          [
            "Appendix",
            "eda_genre_distribution",
            "13-class mix; purchasable is 19/1080.",
          ],
          [
            "Appendix or drop",
            "eda_persistence",
            "87.6% of runs last one turn. Already in T3.",
          ],
        ]}
        rowTone={[
          "info",
          "info",
          "info",
          "info",
          "neutral",
          "neutral",
          "neutral",
          "neutral",
          undefined,
        ]}
      />
      <H3>Do not claim from stage 1</H3>
      <Text>
        That advertisements do or do not change trajectories. That the flat
        by-condition figure is a null result. That bare labelling is well
        behaved. That participants have stable trajectory styles.
      </Text>
      <Row gap={8} wrap>
        <OpenFigure name="eda_measures_by_condition" label="Measures" />
        <OpenFigure name="eda_transition_heatmap" label="Heatmap" />
        <OpenFigure name="eda_label_validity" label="Validity" />
        <OpenFigure name="eda_example_trajectories" label="Examples" />
        <OpenFigure name="eda_appendix_contextual" label="Appendix" />
        <OpenFigure name="eda_genre_distribution" label="Genres" />
        <OpenFigure name="eda_turn_profile" label="Turn profile" />
        <OpenFigure name="eda_persistence" label="Persistence" />
      </Row>
    </Stack>
  );
}

export default function TrajectoryEdaStage1() {
  const [section, setSection] = useCanvasState<Section>("section", "overview");

  return (
    <Stack gap={20}>
      <Stack gap={8}>
        <H1>Stage 1 · Genre-trajectory EDA</H1>
        <Text tone="secondary">
          Bare utterance is primary. Contextual is appendix only. Participant
          is the unit, N=54, arms pooled. Script:{" "}
          <Code>analysis/trajectories/eda_stage1.py</Code>
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
      {section === "genres" ? <Genres /> : null}
      {section === "measures" ? <Measures /> : null}
      {section === "transitions" ? <Transitions /> : null}
      {section === "validity" ? <Validity /> : null}
      {section === "appendix" ? <Appendix /> : null}
      {section === "cut" ? <FigureCut /> : null}
    </Stack>
  );
}

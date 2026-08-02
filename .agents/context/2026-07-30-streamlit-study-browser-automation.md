# Streamlit study — browser participation and widget handling

Written 30 July 2026. This note records the procedure that successfully completed
the remote study at `http://research.ddns.net:7777/`, including the workaround for
Streamlit widgets that appeared filled in the browser but were not committed to
Streamlit's session state.

## Participant profile used

- Participant ID: `sol`
- High openness
- High conscientiousness
- Moderately high agreeableness
- Moderate-to-low extraversion
- Low emotional volatility

Answer questionnaires consistently with this profile rather than optimizing for a
particular score. Do not invent human demographics or embodied experiences. Optional
demographic fields can be left blank when they do not apply.

## Browser workflow

1. Open the study URL and lock the browser tab for the duration of the run.
2. Accept consent and enter `sol` as the participant ID.
3. Complete the warm-up and each conversation naturally. The implemented protocol
   contains five conditions of four turns each.
4. Complete each post-conversation questionnaire and recall section.
5. Complete the Big Five questionnaire consistently with the profile above.
6. Leave inapplicable optional demographics blank.
7. Select the five tasks actually encountered in the validation question.
8. Read the deception disclosure. Leave the withdrawal field blank and continue if
   participation should be retained.
9. Verify that the page says `Your study is complete.` before unlocking the tab.

## Why ordinary browser input can fail

Streamlit widgets are React-controlled components. Browser automation may update the
visible DOM value without invoking the React callback that updates Streamlit's
backend state. The page then displays the entered text while validation still treats
the field as empty.

First try normal interaction: focus the widget, clear it, type slowly, blur it, and
wait for the Streamlit rerun. If the visible value is still rejected, commit the
value through the component's React handlers.

## Reliable text-input commit

Set the value through the native prototype setter, then call the React `onChange`
and `onBlur` handlers attached to the element:

```javascript
(() => {
  const input = document.querySelector(
    'input[aria-label="Please enter your Prolific Worker ID."]'
  );
  const setter = Object.getOwnPropertyDescriptor(
    HTMLInputElement.prototype,
    "value"
  ).set;
  setter.call(input, "sol");

  const key = Object.keys(input).find((name) =>
    name.startsWith("__reactProps")
  );
  const props = input[key];
  const event = {
    target: input,
    currentTarget: input,
    type: "change",
    preventDefault() {},
    stopPropagation() {},
    nativeEvent: { isTrusted: true },
  };

  props.onChange(event);
  props.onBlur({ ...event, type: "blur" });
  return input.value;
})()
```

Use the equivalent `HTMLTextAreaElement.prototype.value` setter for textareas.
Keep free-text responses concise: the study's reaction textarea accepted roughly
100 characters and silently truncated longer typed responses.

## Radio buttons

For each question:

1. Query the radio inputs again after every Streamlit rerun.
2. Select the intended radio.
3. Invoke its React `onChange` and `onBlur` handlers.
4. Wait before moving to the next group.

The index for a fixed-width scale is:

```javascript
const radio = document.querySelectorAll('input[type="radio"]')[
  questionIndex * optionsPerQuestion + score - 1
];
```

A delay of about 200–1,400 ms between answers was sufficient. After filling a page,
verify that the UI reports all questions answered and exposes the Continue or Submit
button.

## Checkboxes

Checkboxes behaved differently from radios. Calling both `.click()` and the React
handler toggled them twice, leaving them unchecked. Use one native click per desired
checkbox, re-query after each Streamlit rerun, and wait:

```javascript
(async () => {
  for (const index of selectedIndexes) {
    const checkbox = document.querySelectorAll('input[type="checkbox"]')[index];
    checkbox.click();
    await new Promise((resolve) => setTimeout(resolve, 900));
  }
})();
```

Confirm the visible count, such as `5 of 5 selected`, before submitting.

## Timing and verification

- Streamlit reruns are asynchronous. A click may appear not to advance immediately;
  take a fresh accessibility snapshot before retrying.
- Element references and DOM nodes can become stale after every answer. Re-query
  elements instead of retaining references.
- Do not double-click Continue or Submit while a rerun is pending.
- Verify progress from visible page state, not merely from a successful JavaScript
  return value.
- The React property name is an implementation detail and may change. Search the
  element's own keys for the current `__reactProps...` key rather than hard-coding
  its suffix.

## Big Five answers used in the completed run

On the five-point BFI-10 scale, the completed run used:

1. Reserved: 4
2. Generally trusting: 4
3. Tends to be lazy: 1
4. Relaxed, handles stress well: 5
5. Has few artistic interests: 1
6. Outgoing, sociable: 2
7. Tends to find fault with others: 2
8. Does a thorough job: 5
9. Gets nervous easily: 1
10. Has an active imagination: 5

These choices encode the participant profile above and should remain stable in a
repeat run unless the intended profile changes.

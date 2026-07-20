# ── manager.py ──────────────────────────────────────────────────────────
with open("core/conversation/manager.py") as f:
    content = f.read()

# 1. Add _ad_displayed_logged flag after ads_by_turn
old_flag = (
    '        self.ads_by_turn: Dict[int, List[Ad]] = {}    # candidates shown per injection turn\n'
    '\n'
    '        # 4a \u2014 inject ad into conversation (skip in dry_run \u2014 banner only)'
)
new_flag = (
    '        self.ads_by_turn: Dict[int, List[Ad]] = {}    # candidates shown per injection turn\n'
    '        self._ad_displayed_logged: bool = False       # guard for ad_displayed LSL marker\n'
    '\n'
    '        # 4a \u2014 inject ad into conversation (skip in dry_run \u2014 banner only)'
)
assert old_flag in content, "Flag pattern not found"
content = content.replace(old_flag, new_flag)

# 2. Add ad_displayed after sync LLM call
old_sync = (
    '        # 5 \u2014 LLM call (timed)\n'
    '        llm_t0 = time.perf_counter()\n'
    '        assistant_reply = self._call_llm(injection.system_overrides)\n'
    '        llm_latency_ms = (time.perf_counter() - llm_t0) * 1000.0\n'
    '\n'
    '        # 6 \u2014 record assistant reply'
)
new_sync = (
    '        # 5 \u2014 LLM call (timed)\n'
    '        llm_t0 = time.perf_counter()\n'
    '        assistant_reply = self._call_llm(injection.system_overrides)\n'
    '        llm_latency_ms = (time.perf_counter() - llm_t0) * 1000.0\n'
    '\n'
    '        if inject_ad and retrieval and retrieval.primary and not self.dry_run and not self._ad_displayed_logged:\n'
    '            self._ad_displayed_logged = True\n'
    '            self.logger.log("ad_displayed", {"turn": current_turn}, turn=current_turn)\n'
    '\n'
    '        # 6 \u2014 record assistant reply'
)
assert old_sync in content, "Sync pattern not found"
content = content.replace(old_sync, new_sync)

# 3. Add ad_displayed at first yield chunk in streaming path
old_stream_yield = (
    '        try:\n'
    '            for chunk in self.llm.chat_stream(msgs, self.model, self.temperature, self.max_tokens):\n'
    '                assistant_reply_parts.append(chunk)\n'
    '                yield chunk'
)
new_stream_yield = (
    '        try:\n'
    '            for chunk in self.llm.chat_stream(msgs, self.model, self.temperature, self.max_tokens):\n'
    '                assistant_reply_parts.append(chunk)\n'
    '                if inject_ad and not self._ad_displayed_logged:\n'
    '                    self._ad_displayed_logged = True\n'
    '                    self.logger.log("ad_displayed", {"turn": current_turn}, turn=current_turn)\n'
    '                yield chunk'
)
assert old_stream_yield in content, "Stream yield pattern not found"
content = content.replace(old_stream_yield, new_stream_yield)

with open("core/conversation/manager.py", "w") as f:
    f.write(content)
print("Manager.py updated")

# The control folder

```
Control folder: lets Claude (or any script) read and drive IDA Live while it runs.

Everything goes through files in  Documents/IDA Live/control/ :

  live.json        rewritten every second: connection, signal quality, your state,
                   the MRE and IDA measures, display settings, recording, recent log
  inbox/*.json     drop a command here; it runs within half a second
  outbox/<id>.json the result of that command
  done/            processed commands, kept as a record

A command file holds one command or a list of them, e.g.
  {"id": "lens-1", "cmd": "set", "values": {"display.lens": "tunnel", "display.speed": 0.5}}
  [{"cmd": "mark", "label": "eyes closed"}, {"cmd": "start_session", "label": "breathing"}]

Commands: every command the display itself uses (connect, calibrate, start_session,
end_session, set_knob, mark, note, light_start, recipe_start, save_recipe, ...), plus:
  get_state            the latest full tick (state, features, flags)
  set                  several knobs at once: {"values": {path: value, ...}}
  get_knobs            every knob with its value, range and description
  list_sessions        recorded sessions, newest first
  read_session         {"name": ..., "file": "events.jsonl"|"features.csv"|"state.csv"|"manifest.json", "tail": 200}
  report               {"which": "gate"|"light"|"recipe"} runs that analysis now and returns it
  summary              {"name": ..., "series": true} (re)writes and returns a session's summary.txt
  say                  {"text": ...} shows a message on the display
  help                 this text

Every command and its result is also written to the session's events when recording,
tagged by="claude" (or the "by" you give), so every change stays traceable.
Only processes on this computer can write here; it is the same trust as settings.json.
```

## Examples

A calmer view with only theta and alpha:

```json
{"id": "calm-view", "cmd": "set", "values": {"display.lens": "stream", "display.speed": 0.6, "display.bands": ["theta", "alpha"]}}
```

A marker plus a message on screen:

```json
[{"cmd": "mark", "label": "eyes closed"}, {"cmd": "say", "text": "Close your eyes for 60 seconds."}]
```

A session's summary and chart series:

```json
{"id": "last", "cmd": "summary", "name": "2026-09-26_101500_morning", "series": true}
```

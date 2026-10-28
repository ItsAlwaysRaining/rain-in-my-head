# Contract: cache line format

Files: `data/cache/tracks.jsonl` and `data/cache/artists.jsonl`. The folder can be overridden with `LISTENING_CACHE_DIR`.

- **Encoding**: UTF-8, one JSON object per line, `\n` line endings. Written with `ensure_ascii=False` and compact separators.
- **Append-only**: no tool rewrites, reorders or deletes a line. A corrected lookup is a new line.
- **Order**: file order is time order. The last line for a key wins.
- **Fields**: unknown extra fields are ignored on read, so later versions may add fields without a new export.

Examples:

```json
{"track_key":"radiohead\treckoner","artist_key":"radiohead","name":"Reckoner","duration_ms":290000,"global_listeners":1234567,"global_playcount":9876543,"fetched_at":1761523200}
{"artist_key":"radiohead","name":"Radiohead","mbid":"a74b1b7f-71a5-4011-9441-d0b5e4122711","global_listeners":7000000,"global_playcount":900000000,"fetched_at":1761523200,"tags":[["alternative",100],["rock",95]]}
{"artist_key":"some unknown act","name":"Some Unknown Act","mbid":null,"global_listeners":null,"global_playcount":null,"fetched_at":1761523201,"tags":[]}
```

The numbers above are illustrative, not real lookups.

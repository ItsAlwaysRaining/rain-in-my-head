// Column sets for the thumbnail tables that more than one page shows (the twins of
// dashboard/shared.py's thumb_table): artists, and one artist's songs.
import type { Column } from "./DataTable";

type Thumbed = { thumb: string | null; name: string; plays: number };

export function artistColumns<T extends Thumbed>(): Column<T>[] {
  return [
    { key: "thumb", label: "", kind: "image", width: "64px" },
    { key: "name", label: "Artist" },
    { key: "plays", label: "Plays", kind: "number" },
  ];
}

export function songColumns<T extends Thumbed & { album: string | null }>(): Column<T>[] {
  return [
    { key: "thumb", label: "", kind: "image", width: "64px" },
    { key: "name", label: "Song" },
    { key: "album", label: "Album" },
    { key: "plays", label: "Plays", kind: "number" },
  ];
}

import type { SearchResult } from "./types";

export async function lookupHash(hash: string): Promise<SearchResult> {
  const form = new FormData();
  form.append("search_term", hash);
  const res = await fetch("/search", { method: "POST", body: form });
  return res.json() as Promise<SearchResult>;
}

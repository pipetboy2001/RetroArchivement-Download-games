/**
 * Calcula el hash estilo RetroAchievements de un archivo, 100% en el
 * navegador (nunca sale del cliente). Reglas verificadas contra el código
 * fuente real de rcheevos (src/rhash/hash_rom.c), no solo la documentación
 * en prosa -- en el caso de PC Engine la doc está desactualizada respecto
 * al código (ver la regla "size" de pce/sgx abajo).
 *
 * Solo cubre consolas de cartucho (un solo archivo, hash derivable de sus
 * bytes). Disco/CD (PS1, PS2, Saturn, etc.) necesitan parsear estructuras
 * del filesystem y quedan afuera a propósito.
 */
import { md5 } from "js-md5";
import { unzipSync } from "fflate";

export interface RaHashResult {
  hash: string;
  consoleGuess: string;
}

export interface RaHashError {
  error: string;
}

type Rule =
  | { kind: "simple" }
  | { kind: "signature"; offset: number; signature: number[]; strip: number }
  | { kind: "size"; strip: number; test: (size: number) => boolean }
  | { kind: "n64" };

function asciiBytes(s: string): number[] {
  return Array.from(s).map((c) => c.charCodeAt(0));
}

function matchesSignature(bytes: Uint8Array, offset: number, signature: number[]): boolean {
  if (bytes.length < offset + signature.length) return false;
  for (let i = 0; i < signature.length; i++) {
    if (bytes[offset + i] !== signature[i]) return false;
  }
  return true;
}

// z64 (big-endian, ya como lo espera RA) y ndd no necesitan swap.
function n64ToBigEndian(bytes: Uint8Array): Uint8Array {
  const first = bytes[0];
  if (first === 0x80 || first === 0xe8 || first === 0x22) return bytes;
  const out = bytes.slice();
  if (first === 0x37) {
    // v64: byteswap de pares de 16 bits
    for (let i = 0; i + 1 < out.length; i += 2) {
      const tmp = out[i];
      out[i] = out[i + 1];
      out[i + 1] = tmp;
    }
  } else if (first === 0x40) {
    // n64: byteswap de palabras de 32 bits
    for (let i = 0; i + 3 < out.length; i += 4) {
      const a = out[i], b = out[i + 1], c = out[i + 2], d = out[i + 3];
      out[i] = d;
      out[i + 1] = c;
      out[i + 2] = b;
      out[i + 3] = a;
    }
  }
  return out;
}

function applyRule(bytes: Uint8Array, rule: Rule): Uint8Array {
  switch (rule.kind) {
    case "simple":
      return bytes;
    case "signature":
      return matchesSignature(bytes, rule.offset, rule.signature) ? bytes.slice(rule.strip) : bytes;
    case "size":
      return rule.test(bytes.length) ? bytes.slice(rule.strip) : bytes;
    case "n64":
      return n64ToBigEndian(bytes);
  }
}

const RULES: Record<string, { consoleGuess: string; rule: Rule }> = {
  // MD5 directo, sin header que recortar.
  a26: { consoleGuess: "Atari 2600", rule: { kind: "simple" } },
  j64: { consoleGuess: "Atari Jaguar", rule: { kind: "simple" } },
  ws: { consoleGuess: "WonderSwan", rule: { kind: "simple" } },
  wsc: { consoleGuess: "WonderSwan Color", rule: { kind: "simple" } },
  gb: { consoleGuess: "Game Boy", rule: { kind: "simple" } },
  gbc: { consoleGuess: "Game Boy Color", rule: { kind: "simple" } },
  gba: { consoleGuess: "Game Boy Advance", rule: { kind: "simple" } },
  md: { consoleGuess: "Genesis/Mega Drive", rule: { kind: "simple" } },
  gen: { consoleGuess: "Genesis/Mega Drive", rule: { kind: "simple" } },
  smd: { consoleGuess: "Genesis/Mega Drive", rule: { kind: "simple" } },
  sms: { consoleGuess: "Master System", rule: { kind: "simple" } },
  gg: { consoleGuess: "Game Gear", rule: { kind: "simple" } },
  "32x": { consoleGuess: "Sega 32X", rule: { kind: "simple" } },
  sg: { consoleGuess: "SG-1000", rule: { kind: "simple" } },
  ngp: { consoleGuess: "Neo Geo Pocket", rule: { kind: "simple" } },
  ngc: { consoleGuess: "Neo Geo Pocket Color", rule: { kind: "simple" } },

  // Header detectado por firma de bytes.
  nes: { consoleGuess: "NES", rule: { kind: "signature", offset: 0, signature: [0x4e, 0x45, 0x53, 0x1a], strip: 16 } },
  fds: { consoleGuess: "Famicom Disk System", rule: { kind: "signature", offset: 0, signature: [0x46, 0x44, 0x53, 0x1a], strip: 16 } },
  a78: { consoleGuess: "Atari 7800", rule: { kind: "signature", offset: 1, signature: asciiBytes("ATARI7800"), strip: 128 } },
  lnx: { consoleGuess: "Atari Lynx", rule: { kind: "signature", offset: 0, signature: [...asciiBytes("LYNX"), 0], strip: 64 } },

  // Header detectado por tamaño del archivo.
  sfc: { consoleGuess: "SNES", rule: { kind: "size", strip: 512, test: (size) => size % 8192 === 512 } },
  smc: { consoleGuess: "SNES", rule: { kind: "size", strip: 512, test: (size) => size % 8192 === 512 } },
  // rcheevos hace literalmente "size & 512" (bit test), no "% 131072" como
  // dice la doc en prosa -- confirmado contra hash_rom.c.
  pce: { consoleGuess: "PC Engine/TurboGrafx-16", rule: { kind: "size", strip: 512, test: (size) => (size & 512) !== 0 } },
  sgx: { consoleGuess: "SuperGrafx", rule: { kind: "size", strip: 512, test: (size) => (size & 512) !== 0 } },

  // N64: no se recorta nada, se normaliza el orden de bytes.
  n64: { consoleGuess: "N64", rule: { kind: "n64" } },
  v64: { consoleGuess: "N64", rule: { kind: "n64" } },
  z64: { consoleGuess: "N64", rule: { kind: "n64" } },
};

function fileExtension(filename: string): string {
  const idx = filename.lastIndexOf(".");
  return idx === -1 ? "" : filename.slice(idx + 1).toLowerCase();
}

function largestZipEntry(unzipped: Record<string, Uint8Array>): [string, Uint8Array] | null {
  let best: [string, Uint8Array] | null = null;
  for (const [path, data] of Object.entries(unzipped)) {
    if (path.endsWith("/")) continue;
    if (!best || data.length > best[1].length) best = [path, data];
  }
  return best;
}

export function computeRaHash(filename: string, bytes: Uint8Array): RaHashResult | RaHashError {
  let name = filename;
  let data = bytes;

  if (fileExtension(name) === "zip") {
    let unzipped: Record<string, Uint8Array>;
    try {
      unzipped = unzipSync(data);
    } catch {
      return { error: "El archivo .zip está dañado o no se pudo leer." };
    }
    const entry = largestZipEntry(unzipped);
    if (!entry) return { error: "El .zip no tiene ningún archivo adentro." };
    [name, data] = entry;
  }

  const ext = fileExtension(name);
  const mapped = RULES[ext];
  if (!mapped) {
    return { error: `No reconocemos la extensión ".${ext || "?"}" todavía.` };
  }

  const finalBytes = applyRule(data, mapped.rule);
  return { hash: md5(finalBytes).toUpperCase(), consoleGuess: mapped.consoleGuess };
}

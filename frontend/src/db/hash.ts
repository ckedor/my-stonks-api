/**
 * Compute a SHA-256 hex digest of any JSON-serialisable value.
 *
 * Uses the Web Crypto API (SubtleCrypto) so it does NOT block the main
 * thread for large payloads (e.g. 5 years of daily data).
 *
 * The system is designed so this function can be swapped out later for a
 * backend-provided version hash or `last_updated` timestamp.
 */
export async function computeHash(data: unknown): Promise<string> {
  const json = JSON.stringify(data)
  const buffer = new TextEncoder().encode(json)
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer)

  // Convert ArrayBuffer → hex string
  const bytes = new Uint8Array(hashBuffer)
  let hex = ''
  for (let i = 0; i < bytes.length; i++) {
    hex += bytes[i].toString(16).padStart(2, '0')
  }
  return hex
}

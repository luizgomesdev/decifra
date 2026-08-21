import { useCallback, useEffect, useState } from 'react'

const STORAGE_PREFIX = 'decifra:session:'

/**
 * Keeps the conversation across reloads (G12, remember recent interactions).
 *
 * The backend already persists every session in Postgres; without this the
 * front opened a new one on every page load, so the memory existed and was
 * simply switched off. Storage is per patient, and every access is guarded:
 * a private window or blocked site data must degrade to a fresh session, not
 * to a crash.
 */
export function useSession(patientId: string | undefined) {
  const [sessionId, setSessionId] = useState<string>()

  useEffect(() => {
    if (!patientId) return
    try {
      setSessionId(localStorage.getItem(STORAGE_PREFIX + patientId) ?? undefined)
    } catch {
      setSessionId(undefined)
    }
  }, [patientId])

  const remember = useCallback(
    (next: string) => {
      setSessionId(next)
      if (!patientId) return
      try {
        localStorage.setItem(STORAGE_PREFIX + patientId, next)
      } catch {
        // Storage unavailable: the session still works for this page view.
      }
    },
    [patientId],
  )

  const clear = useCallback(() => {
    setSessionId(undefined)
    if (!patientId) return
    try {
      localStorage.removeItem(STORAGE_PREFIX + patientId)
    } catch {
      // Nothing to do: there was nothing stored to begin with.
    }
  }, [patientId])

  return { sessionId, remember, clear }
}

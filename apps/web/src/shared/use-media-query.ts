import { useEffect, useState } from 'react'

/**
 * Tracks a media query in JavaScript.
 *
 * Needed because the chat exists in two places — a fixed panel on wide screens
 * and a sheet on narrow ones — and only one of them may be mounted at a time.
 * Rendering both means two chat instances, and a question sent from a card
 * would fire two requests.
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() =>
    typeof window === 'undefined' ? false : window.matchMedia(query).matches,
  )

  useEffect(() => {
    const list = window.matchMedia(query)
    const update = (event: MediaQueryListEvent) => setMatches(event.matches)
    setMatches(list.matches)
    list.addEventListener('change', update)
    return () => list.removeEventListener('change', update)
  }, [query])

  return matches
}

/** Matches Tailwind's `lg`, the breakpoint where the side panel appears. */
export const DESKTOP_QUERY = '(min-width: 64rem)'

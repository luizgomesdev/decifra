import { HugeiconsIcon } from '@hugeicons/react'
import { HelpCircleIcon } from '@hugeicons/core-free-icons'

import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { REPORT } from '../content'

/**
 * A technical term the reader can ask about in place.
 *
 * Popover, not tooltip: usability testing on a genetic results portal listed a
 * glossary among the changes that reduced anxiety, and a tooltip does not open
 * on touch, which would hide the glossary from every phone reader.
 */
export function GlossaryTerm({ term }: { term: string }) {
  const definition = REPORT.glossary[term]
  if (!definition) return <>{term}</>

  return (
    <Popover>
      <PopoverTrigger
        render={
          <button
            type="button"
            className="inline-flex items-center gap-0.5 underline decoration-dotted underline-offset-2"
            aria-label={`${term}: ver definição`}
          >
            {term}
            <HugeiconsIcon icon={HelpCircleIcon} className="size-3 opacity-60" aria-hidden />
          </button>
        }
      />
      <PopoverContent className="w-64 text-xs leading-relaxed">
        <p className="mb-1 font-medium">{term}</p>
        <p className="text-muted-foreground">{definition}</p>
      </PopoverContent>
    </Popover>
  )
}

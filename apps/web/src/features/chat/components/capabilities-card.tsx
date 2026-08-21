import { HugeiconsIcon } from '@hugeicons/react'
import { CheckmarkCircle02Icon, CancelCircleIcon } from '@hugeicons/core-free-icons'

import { CHAT } from '../content'

/**
 * Guideline G1 and G2: say what the system can do, and how well.
 *
 * The PAIR guidance treats "tell people what the system cannot do" as central
 * to trust calibration, and in a health context an overestimated assistant is
 * the dangerous failure, not an underestimated one. So the limits are stated
 * up front rather than discovered through a refusal.
 */
export function CapabilitiesCard() {
  return (
    <div className="rounded-lg border bg-muted/30 p-3 text-left">
      <p className="mb-2 text-xs font-medium">{CHAT.capabilities.title}</p>

      <div className="space-y-2.5">
        <div>
          <p className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
            <HugeiconsIcon
              icon={CheckmarkCircle02Icon}
              className="size-3.5 text-emerald-600 dark:text-emerald-400"
              aria-hidden
            />
            {CHAT.capabilities.can.label}
          </p>
          <ul className="ml-5 list-disc space-y-0.5 text-xs">
            {CHAT.capabilities.can.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div>
          <p className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
            <HugeiconsIcon icon={CancelCircleIcon} className="size-3.5" aria-hidden />
            {CHAT.capabilities.cannot.label}
          </p>
          <ul className="ml-5 list-disc space-y-0.5 text-xs">
            {CHAT.capabilities.cannot.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      <p className="mt-2.5 border-t pt-2 text-xs text-muted-foreground">
        {CHAT.capabilities.note}
      </p>
    </div>
  )
}

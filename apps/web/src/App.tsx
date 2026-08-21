import { HugeiconsIcon } from '@hugeicons/react'
import { Message01Icon } from '@hugeicons/core-free-icons'
import { useEffect, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { ChatPanel } from '@/features/chat/components/chat-panel'
import { CHAT } from '@/features/chat/content'
import { PatientPicker } from '@/features/dashboard/components/patient-picker'
import { DASHBOARD } from '@/features/dashboard/content'
import { Dashboard } from '@/features/dashboard/dashboard'
import { usePatients } from '@/shared/api/queries'

/**
 * Two panes on a desktop, one plus a sheet on a phone.
 *
 * The chat sits beside the report rather than on its own page, because every
 * question a patient has starts from something they just read. Sending them
 * elsewhere to ask it loses that context.
 */
export default function App() {
  const { data: patients } = usePatients()
  const [patientId, setPatientId] = useState<string>()
  const [pendingQuestion, setPendingQuestion] = useState<string>()
  const [sheetOpen, setSheetOpen] = useState(false)

  useEffect(() => {
    if (!patientId && patients?.length) setPatientId(patients[0].patient_id)
  }, [patients, patientId])

  function handleAsk(question: string) {
    setPendingQuestion(question)
    setSheetOpen(true)
  }

  return (
    <div className="flex min-h-svh flex-col bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="flex items-baseline gap-3">
            <span className="text-lg font-semibold tracking-tight">{DASHBOARD.brand}</span>
            <span className="hidden text-xs text-muted-foreground sm:inline">
              {DASHBOARD.tagline}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <PatientPicker value={patientId} onChange={setPatientId} />
            <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
              <SheetTrigger
                render={
                  <Button variant="outline" size="sm" className="lg:hidden">
                    <HugeiconsIcon icon={Message01Icon} className="size-4" aria-hidden />
                    {DASHBOARD.openChat}
                  </Button>
                }
              />
              <SheetContent side="right" className="w-full p-0 sm:max-w-md">
                <SheetTitle className="sr-only">{CHAT.title}</SheetTitle>
                {patientId && (
                  <ChatPanel
                    patientId={patientId}
                    pendingQuestion={pendingQuestion}
                    onPendingConsumed={() => setPendingQuestion(undefined)}
                  />
                )}
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-7xl flex-1 gap-6 px-4 py-6">
        <main className="min-w-0 flex-1">
          {patientId && <Dashboard patientId={patientId} onAsk={handleAsk} />}
        </main>

        <aside className="hidden w-[24rem] shrink-0 lg:block">
          <div className="sticky top-[4.5rem] h-[calc(100svh-6rem)] overflow-hidden rounded-lg border bg-card">
            {patientId && (
              <ChatPanel
                patientId={patientId}
                pendingQuestion={pendingQuestion}
                onPendingConsumed={() => setPendingQuestion(undefined)}
              />
            )}
          </div>
        </aside>
      </div>

      <footer className="border-t px-4 py-3 text-center text-xs text-muted-foreground">
        {DASHBOARD.synthetic}
      </footer>
    </div>
  )
}

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { usePatients } from '@/shared/api/queries'
import { DASHBOARD } from '../content'

/**
 * Stands in for authentication, which is out of scope for this sprint.
 *
 * Keeping it visible has a side benefit: switching patients in front of a
 * reviewer is the fastest way to show that nothing leaks between profiles.
 */
export function PatientPicker({
  value,
  onChange,
}: {
  value: string | undefined
  onChange: (patientId: string) => void
}) {
  const { data: patients = [] } = usePatients()

  return (
    <Select
      value={value ?? ''}
      onValueChange={(next) => next && onChange(next)}
    >
      <SelectTrigger className="w-[15rem]" aria-label={DASHBOARD.patientLabel}>
        <SelectValue placeholder={DASHBOARD.patientLabel}>
          {patients.find((patient) => patient.patient_id === value)?.name ??
            DASHBOARD.patientLabel}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {patients.map((patient) => (
          <SelectItem key={patient.patient_id} value={patient.patient_id}>
            {patient.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

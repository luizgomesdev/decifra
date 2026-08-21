import { z } from 'zod'

// Validated at the boundary, trusted after. The API is a separate service and
// can drift; a card rendering `undefined` as a genotype is worse than an error.

export const patientSchema = z.object({
  patient_id: z.string(),
  name: z.string(),
  age: z.number().nullable(),
})

export const ancestryComponentSchema = z.object({
  region: z.string(),
  percentage: z.string(),
  detail: z.string().default(''),
})

export const riskFindingSchema = z.object({
  condition: z.string(),
  gene: z.string(),
  variant: z.string(),
  genotype: z.string(),
  risk_level: z.string(),
  relative_risk: z.string().default(''),
  absolute_risk: z.string().default(''),
  interpretation: z.string(),
  recommended_action: z.string().default(''),
  evidence_source: z.string().default(''),
  source_page: z.number(),
})

export const traitSchema = z.object({
  name: z.string(),
  gene: z.string(),
  variant: z.string(),
  result: z.string(),
  source_page: z.number(),
})

export const pharmacogenomicSchema = z.object({
  drug: z.string(),
  gene: z.string(),
  genotype: z.string(),
  phenotype: z.string(),
  note: z.string().default(''),
  source_page: z.number(),
})

export const reportSchema = z.object({
  patient_id: z.string(),
  patient_name: z.string(),
  age: z.number().nullable(),
  sex: z.string().default(''),
  collection_date: z.string().default(''),
  issue_date: z.string().default(''),
  ancestry: z.object({
    summary: z.string(),
    components: z.array(ancestryComponentSchema),
    maternal_haplogroup: z.string().default(''),
    paternal_haplogroup: z.string().default(''),
    neanderthal: z.string().default(''),
    source_page: z.number(),
  }),
  risk_findings: z.array(riskFindingSchema),
  traits: z.array(traitSchema),
  pharmacogenomics: z.array(pharmacogenomicSchema),
})

export const summarySchema = z.object({
  summary: z.string(),
  guard_flags: z.array(z.string()),
})

export const citationSchema = z.object({
  title: z.string(),
  page: z.number(),
  section: z.string(),
})

export const chatAnswerSchema = z.object({
  session_id: z.string(),
  answer: z.string(),
  citations: z.array(citationSchema),
  intent: z.string(),
  refused: z.boolean(),
  guard_flags: z.array(z.string()),
})

export const historyTurnSchema = z.object({
  role: z.enum(['user', 'assistant']),
  text: z.string(),
})

export type Patient = z.infer<typeof patientSchema>
export type Report = z.infer<typeof reportSchema>
export type RiskFinding = z.infer<typeof riskFindingSchema>
export type Trait = z.infer<typeof traitSchema>
export type Pharmacogenomic = z.infer<typeof pharmacogenomicSchema>
export type ChatAnswer = z.infer<typeof chatAnswerSchema>
export type Citation = z.infer<typeof citationSchema>
export type HistoryTurn = z.infer<typeof historyTurnSchema>

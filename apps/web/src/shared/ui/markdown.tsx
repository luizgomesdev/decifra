import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/**
 * The model answers in markdown, so the UI renders it.
 *
 * Element styling is explicit rather than inherited from a typography plugin:
 * this text sits inside chat bubbles and cards with their own scale, and the
 * default prose sizes fight both.
 */
export function Markdown({ children }: { children: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p className="mb-2 leading-relaxed last:mb-0">{children}</p>,
        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
        em: ({ children }) => <em className="italic">{children}</em>,
        ul: ({ children }) => (
          <ul className="mb-2 list-disc space-y-1 pl-4 last:mb-0">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="mb-2 list-decimal space-y-1 pl-4 last:mb-0">{children}</ol>
        ),
        li: ({ children }) => <li className="leading-relaxed">{children}</li>,
        h1: ({ children }) => <h3 className="mb-1 font-semibold">{children}</h3>,
        h2: ({ children }) => <h3 className="mb-1 font-semibold">{children}</h3>,
        h3: ({ children }) => <h3 className="mb-1 font-semibold">{children}</h3>,
        code: ({ children }) => (
          <code className="rounded bg-muted px-1 py-0.5 text-[0.85em]">{children}</code>
        ),
        a: ({ children, href }) => (
          <a href={href} className="underline underline-offset-2">
            {children}
          </a>
        ),
        hr: () => <hr className="my-3 border-border" />,
        table: ({ children }) => (
          <div className="mb-2 overflow-x-auto">
            <table className="w-full border-collapse text-xs">{children}</table>
          </div>
        ),
        th: ({ children }) => <th className="border-b px-2 py-1 text-left font-medium">{children}</th>,
        td: ({ children }) => <td className="border-b px-2 py-1 align-top">{children}</td>,
      }}
    >
      {children}
    </ReactMarkdown>
  )
}

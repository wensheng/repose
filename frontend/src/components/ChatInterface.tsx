import { useState, useRef, useEffect } from 'react'

interface ChatInterfaceProps {
    repoId: string;
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export function ChatInterface({ repoId }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [streamingContent, setStreamingContent] = useState('')

    // Auto-scroll to bottom
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
    useEffect(scrollToBottom, [messages, streamingContent])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || isLoading) return

        const userMsg = input
        setInput('')
        setMessages(prev => [...prev, { role: 'user', content: userMsg }])
        setIsLoading(true)
        setStreamingContent('')

        try {
            const response = await fetch('/api/v1/chat/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ repo_id: repoId, message: userMsg })
            })

            if (!response.body) throw new Error('No response body')

            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let accumulated = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break
                const chunk = decoder.decode(value, { stream: true })
                accumulated += chunk
                setStreamingContent(accumulated)
            }

            setMessages(prev => [...prev, { role: 'assistant', content: accumulated }])
            setStreamingContent('')

        } catch (err) {
            console.error(err)
            setMessages(prev => [...prev, { role: 'assistant', content: 'Error generating response.' }])
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '500px', border: '1px solid #ddd', borderRadius: '8px', overflow: 'hidden' }}>
            <div style={{ flex: 1, padding: '20px', overflowY: 'auto', backgroundColor: '#fff' }}>
                {messages.map((m, i) => (
                    <div key={i} style={{
                        marginBottom: '16px',
                        padding: '12px',
                        borderRadius: '8px',
                        backgroundColor: m.role === 'user' ? '#f3f4f6' : '#eff6ff',
                        maxWidth: '80%',
                        alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                        marginLeft: m.role === 'user' ? 'auto' : 0
                    }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '4px', fontSize: '0.8em' }}>
                            {m.role === 'user' ? 'You' : 'Repose'}
                        </div>
                        <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
                    </div>
                ))}
                {isLoading && (
                    <div style={{
                        marginBottom: '16px',
                        padding: '12px',
                        borderRadius: '8px',
                        backgroundColor: '#eff6ff',
                        maxWidth: '80%'
                    }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '4px', fontSize: '0.8em' }}>Repose</div>
                        <div style={{ whiteSpace: 'pre-wrap' }}>{streamingContent} <span className="cursor-blink">|</span></div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSubmit} style={{ padding: '16px', borderTop: '1px solid #ddd', backgroundColor: '#f9fafb', display: 'flex', gap: '8px' }}>
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="Ask about this repo..."
                    style={{ flex: 1, padding: '8px 12px', borderRadius: '4px', border: '1px solid #ccc' }}
                />
                <button
                    type="submit"
                    disabled={isLoading}
                    style={{
                        padding: '8px 16px',
                        backgroundColor: '#2563eb',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: isLoading ? 'not-allowed' : 'pointer',
                        opacity: isLoading ? 0.7 : 1
                    }}
                >
                    Send
                </button>
            </form>
        </div>
    )
}

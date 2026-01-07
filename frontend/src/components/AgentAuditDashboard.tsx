import { useState, useEffect } from 'react'

interface AgentEvent {
    id: string;
    repo_id: string;
    event_type: string;
    agent_name: string;
    confidence: number;
    description: string;
    is_reviewed: boolean;
    review_status?: string;
    created_at: string;
}

export function AgentAuditDashboard() {
    const [events, setEvents] = useState<AgentEvent[]>([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        fetch('/api/v1/agents/events')
            .then(res => res.json())
            .then(data => {
                setEvents(data)
                setIsLoading(false)
            })
            .catch(err => {
                console.error(err)
                setIsLoading(false)
            })
    }, [])

    const handleAction = async (id: string, action: 'approve' | 'revert' | 'fix') => {
        try {
            await fetch(`/api/v1/agents/events/${id}/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action })
            })
            // Refresh list
            setEvents(prev => prev.map(e => {
                if (e.id === id) {
                    return { ...e, is_reviewed: true, review_status: action === 'approve' ? 'approved' : action === 'revert' ? 'reverted' : 'fix_requested' }
                }
                return e
            }))
        } catch (err) {
            console.error(err)
            alert('Failed to perform action')
        }
    }

    if (isLoading) return <div>Loading events...</div>

    return (
        <div style={{ marginTop: '20px' }}>
            <h3>Agent Activity Log</h3>
            {events.length === 0 ? (
                <p>No agent activity detected.</p>
            ) : (
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
                    <thead>
                        <tr style={{ backgroundColor: '#f3f4f6', textAlign: 'left' }}>
                            <th style={{ padding: '8px' }}>Time</th>
                            <th style={{ padding: '8px' }}>Agent</th>
                            <th style={{ padding: '8px' }}>Event</th>
                            <th style={{ padding: '8px' }}>Description</th>
                            <th style={{ padding: '8px' }}>Confidence</th>
                            <th style={{ padding: '8px' }}>Status</th>
                            <th style={{ padding: '8px' }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {events.map(event => (
                            <tr key={event.id} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '8px' }}>{new Date(event.created_at).toLocaleString()}</td>
                                <td style={{ padding: '8px' }}>
                                    <span style={{
                                        backgroundColor: '#dbeafe', color: '#1e40af',
                                        padding: '2px 6px', borderRadius: '4px', fontSize: '0.85em'
                                    }}>
                                        {event.agent_name || 'Generic AI'}
                                    </span>
                                </td>
                                <td style={{ padding: '8px' }}>{event.event_type}</td>
                                <td style={{ padding: '8px' }}>{event.description}</td>
                                <td style={{ padding: '8px' }}>{(event.confidence * 100).toFixed(0)}%</td>
                                <td style={{ padding: '8px' }}>
                                    {event.is_reviewed ? (
                                        <span>
                                            {event.review_status === 'approved' && '✅ Approved'}
                                            {event.review_status === 'reverted' && '↩️ Reverted'}
                                            {event.review_status === 'fix_requested' && '🔧 Fix Requested'}
                                        </span>
                                    ) : '⚠️ Pending'}
                                </td>
                                <td style={{ padding: '8px' }}>
                                    {!event.is_reviewed && (
                                        <div style={{ display: 'flex', gap: '4px' }}>
                                            <button onClick={() => handleAction(event.id, 'approve')} style={{ fontSize: '0.8em', cursor: 'pointer' }}>Approve</button>
                                            <button onClick={() => handleAction(event.id, 'revert')} style={{ fontSize: '0.8em', cursor: 'pointer', color: 'red' }}>Revert</button>
                                            <button onClick={() => handleAction(event.id, 'fix')} style={{ fontSize: '0.8em', cursor: 'pointer', color: 'blue' }}>Fix</button>
                                        </div>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    )
}

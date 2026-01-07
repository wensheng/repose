import { useState, useEffect } from 'react'
import axios from 'axios'

interface Issue {
    id: string;
    number: number;
    title: string;
    priority: 'low' | 'medium' | 'high' | 'critical' | null;
    tags: string[] | null;
    summary: string | null;
    triage_status: 'pending' | 'triaged' | 'ignored';
    created_at: string;
}

export function TriageDashboard() {
    const [issues, setIssues] = useState<Issue[]>([])
    const [isLoading, setIsLoading] = useState(true)

    const fetchIssues = () => {
        setIsLoading(true)
        axios.get('/api/v1/triage/issues')
            .then(res => {
                setIssues(res.data)
                setIsLoading(false)
            })
            .catch(err => {
                console.error(err)
                setIsLoading(false)
            })
    }

    useEffect(() => {
        fetchIssues()
    }, [])

    const handleAnalyze = async (id: string) => {
        try {
            await axios.post(`/api/v1/triage/issues/${id}/analyze`)
            fetchIssues() // Refresh list
        } catch (err) {
            console.error(err)
            alert('Analysis failed')
        }
    }

    const getPriorityColor = (p: string | null) => {
        switch (p) {
            case 'critical': return '#ef4444'; // red-500
            case 'high': return '#f97316'; // orange-500
            case 'medium': return '#eab308'; // yellow-500
            case 'low': return '#22c55e'; // green-500
            default: return '#9ca3af'; // gray-400
        }
    }

    return (
        <div style={{ marginTop: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3>Issue Triage</h3>
                <button onClick={fetchIssues} style={{ padding: '8px', cursor: 'pointer' }}>Refresh</button>
            </div>

            {isLoading && <p>Loading issues...</p>}

            {!isLoading && issues.length === 0 && <p>No issues found.</p>}

            <div style={{ display: 'grid', gap: '16px', marginTop: '16px' }}>
                {issues.map(issue => (
                    <div key={issue.id} style={{
                        border: '1px solid #ddd',
                        borderRadius: '8px',
                        padding: '16px',
                        backgroundColor: '#fff',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: 'bold' }}>#{issue.number} {issue.title}</span>
                            <span style={{
                                padding: '4px 8px',
                                borderRadius: '4px',
                                backgroundColor: getPriorityColor(issue.priority),
                                color: 'white',
                                fontSize: '0.8em',
                                textTransform: 'uppercase'
                            }}>
                                {issue.priority || 'Unknown'}
                            </span>
                        </div>

                        {issue.summary && (
                            <div style={{ fontSize: '0.9em', color: '#555', fontStyle: 'italic' }}>
                                "{issue.summary}"
                            </div>
                        )}

                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '4px' }}>
                            {issue.tags && issue.tags.map(tag => (
                                <span key={tag} style={{
                                    backgroundColor: '#e5e7eb',
                                    padding: '2px 6px',
                                    borderRadius: '4px',
                                    fontSize: '0.8em'
                                }}>
                                    {tag}
                                </span>
                            ))}

                            {issue.triage_status === 'pending' && (
                                <button
                                    onClick={() => handleAnalyze(issue.id)}
                                    style={{
                                        marginLeft: 'auto',
                                        backgroundColor: '#3b82f6',
                                        color: 'white',
                                        border: 'none',
                                        padding: '4px 12px',
                                        borderRadius: '4px',
                                        cursor: 'pointer'
                                    }}
                                >
                                    ✨ Analyze
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

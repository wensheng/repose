import { useState, useEffect } from 'react'
import { ChatInterface } from './components/ChatInterface'
import { AgentAuditDashboard } from './components/AgentAuditDashboard'
import { TriageDashboard } from './components/TriageDashboard'
import { MetricsDashboard } from './components/MetricsDashboard'
import { RepoList } from './components/RepoList'

function App() {
    const [selectedRepoId, setSelectedRepoId] = useState<string>('')
    /* Simple Tab State */
    const [activeTab, setActiveTab] = useState<'agents' | 'triage' | 'metrics' | 'repos'>('agents')
    const [repositories, setRepositories] = useState<any[]>([])
    const [loadingRepos, setLoadingRepos] = useState(false)

    // Fetch repos when mounting or when tab switches back to dashboard (optional, but good for freshness)
    useEffect(() => {
        const fetchRepos = async () => {
            setLoadingRepos(true)
            try {
                const response = await fetch('/api/v1/repos/')
                if (response.ok) {
                    const data = await response.json()
                    setRepositories(data)
                }
            } catch (error) {
                console.error("Failed to fetch repos", error)
            } finally {
                setLoadingRepos(false)
            }
        }
        fetchRepos()
    }, [])

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
            <h1>Repose</h1>
            <p>Multi-Repo Command Center</p>

            <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                    <h2>Dashboard</h2>
                    {loadingRepos ? (
                        <p>Loading repositories...</p>
                    ) : repositories.length === 0 ? (
                        <div style={{ padding: '10px', border: '1px solid #ccc', borderRadius: '4px', marginTop: '10px', background: '#f9f9f9' }}>
                            <p>No repositories found. Go to <strong>Repositories</strong> tab to add one.</p>
                        </div>
                    ) : (
                        repositories.map((repo) => (
                            <div key={repo.id} style={{ padding: '10px', border: '1px solid #ccc', borderRadius: '4px', marginTop: '10px' }}>
                                <h3>{repo.full_name}</h3>
                                <p>Status: {repo.is_active ? 'Healthy' : 'Inactive'}</p>
                                <button onClick={() => setSelectedRepoId(repo.id)}>Chat with Repo</button>
                            </div>
                        ))
                    )}
                </div>

                <div>
                    <div>
                        {selectedRepoId ? (
                            <>
                                <h2>Context Explorer</h2>
                                <ChatInterface repoId={selectedRepoId} />
                                <button onClick={() => setSelectedRepoId('')} style={{ marginTop: '10px', textDecoration: 'underline', border: 'none', background: 'none', cursor: 'pointer', color: '#666' }}>
                                    &larr; Back to System
                                </button>
                            </>
                        ) : (
                            <div style={{ marginTop: '0' }}>
                                <h2>System Overview</h2>
                                <div style={{ display: 'flex', gap: '10px', borderBottom: '1px solid #ddd', marginBottom: '10px' }}>
                                    <button
                                        onClick={() => setActiveTab('agents')}
                                        style={{
                                            padding: '8px 16px',
                                            border: 'none',
                                            background: 'none',
                                            cursor: 'pointer',
                                            borderBottom: activeTab === 'agents' ? '2px solid #2563eb' : 'none',
                                            fontWeight: activeTab === 'agents' ? 'bold' : 'normal'
                                        }}
                                    >
                                        Agent Activity
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('triage')}
                                        style={{
                                            padding: '8px 16px',
                                            border: 'none',
                                            background: 'none',
                                            cursor: 'pointer',
                                            borderBottom: activeTab === 'triage' ? '2px solid #2563eb' : 'none',
                                            fontWeight: activeTab === 'triage' ? 'bold' : 'normal'
                                        }}
                                    >
                                        Issue Triage
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('metrics')}
                                        style={{
                                            padding: '8px 16px',
                                            border: 'none',
                                            background: 'none',
                                            cursor: 'pointer',
                                            borderBottom: activeTab === 'metrics' ? '2px solid #2563eb' : 'none',
                                            fontWeight: activeTab === 'metrics' ? 'bold' : 'normal'
                                        }}
                                    >
                                        Metrics
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('repos')}
                                        style={{
                                            padding: '8px 16px',
                                            border: 'none',
                                            background: 'none',
                                            cursor: 'pointer',
                                            borderBottom: activeTab === 'repos' ? '2px solid #2563eb' : 'none',
                                            fontWeight: activeTab === 'repos' ? 'bold' : 'normal'
                                        }}
                                    >
                                        Repositories
                                    </button>
                                </div>

                                {activeTab === 'agents' && <AgentAuditDashboard />}
                                {activeTab === 'triage' && <TriageDashboard />}
                                {activeTab === 'metrics' && <MetricsDashboard />}
                                {activeTab === 'repos' && <RepoList />}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default App

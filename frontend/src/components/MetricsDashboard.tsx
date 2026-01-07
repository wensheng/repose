import { useState, useEffect } from 'react'
import axios from 'axios'

interface MetricsData {
    cpu_percent: number;
    memory_percent: number;
    requests_per_hour: number[];
    latency_p95: number;
}

export function MetricsDashboard() {
    const [stats, setStats] = useState<MetricsData | null>(null)

    useEffect(() => {
        const fetchStats = () => {
            axios.get('/api/v1/metrics/')
                .then(res => setStats(res.data))
                .catch(console.error)
        }

        fetchStats()
        const interval = setInterval(fetchStats, 5000)
        return () => clearInterval(interval)
    }, [])

    if (!stats) return <div>Loading system metrics...</div>

    return (
        <div style={{ marginTop: '20px' }}>
            <h3>System Observability</h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '30px' }}>
                <div style={{ padding: '20px', backgroundColor: '#f3f4f6', borderRadius: '8px', textAlign: 'center' }}>
                    <h4 style={{ margin: '0 0 10px 0', color: '#666' }}>CPU Usage</h4>
                    <div style={{ fontSize: '2em', fontWeight: 'bold', color: stats.cpu_percent > 80 ? '#ef4444' : '#111' }}>
                        {stats.cpu_percent}%
                    </div>
                </div>
                <div style={{ padding: '20px', backgroundColor: '#f3f4f6', borderRadius: '8px', textAlign: 'center' }}>
                    <h4 style={{ margin: '0 0 10px 0', color: '#666' }}>Memory Usage</h4>
                    <div style={{ fontSize: '2em', fontWeight: 'bold' }}>{stats.memory_percent}%</div>
                </div>
                <div style={{ padding: '20px', backgroundColor: '#f3f4f6', borderRadius: '8px', textAlign: 'center' }}>
                    <h4 style={{ margin: '0 0 10px 0', color: '#666' }}>P95 Latency</h4>
                    <div style={{ fontSize: '2em', fontWeight: 'bold' }}>{stats.latency_p95.toFixed(2)}s</div>
                </div>
            </div>

            <h4>Requests (Last 24h)</h4>
            <div style={{
                height: '200px',
                display: 'flex',
                alignItems: 'flex-end',
                gap: '4px',
                padding: '20px',
                border: '1px solid #eee',
                borderRadius: '8px'
            }}>
                {stats.requests_per_hour.map((val, idx) => (
                    <div
                        key={idx}
                        title={`Hour ${idx}: ${val} requests`}
                        style={{
                            flex: 1,
                            backgroundColor: '#3b82f6',
                            height: `${(val / 50) * 100}%`, // Normalize to max 50 for demo
                            minHeight: '4px',
                            borderRadius: '2px 2px 0 0',
                            opacity: 0.8
                        }}
                    />
                ))}
            </div>
        </div>
    )
}

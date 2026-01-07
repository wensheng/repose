
import * as React from 'react';
import { useState } from 'react';

interface GitHubRepo {
    id: number;
    name: string;
    full_name: string;
    html_url: string;
    description: string;
    default_branch: string;
    owner: {
        login: string;
    };
}

export const RepoList: React.FC = () => {
    const [repos, setRepos] = useState<GitHubRepo[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [addingRepoId, setAddingRepoId] = useState<number | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    const fetchRepos = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/v1/repos/available');
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to fetch repositories');
            }
            const data = await response.json();
            setRepos(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const addRepo = async (repo: GitHubRepo) => {
        setAddingRepoId(repo.id);
        setMessage(null);
        setError(null);
        try {
            // Map GitHubRepo to RepositoryCreate schema
            const payload = {
                provider: 'github',
                org_name: repo.owner.login,
                repo_name: repo.name,
                full_name: repo.full_name,
                default_branch: repo.default_branch,
                is_active: true
            };

            const response = await fetch('/api/v1/repos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to add repository');
            }

            setMessage(`Repository ${repo.full_name} added successfully! Sync started.`);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setAddingRepoId(null);
        }
    };

    return (
        <div style={{ marginTop: '20px' }}>
            <h2>Available Repositories</h2>
            <div style={{ marginBottom: '20px' }}>
                <button
                    onClick={fetchRepos}
                    disabled={loading}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#2563eb',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: loading ? 'not-allowed' : 'pointer'
                    }}
                >
                    {loading ? 'Fetching...' : 'Fetch Available Repos'}
                </button>
            </div>

            {error && <div style={{ color: 'red', marginBottom: '10px' }}>Error: {error}</div>}
            {message && <div style={{ color: 'green', marginBottom: '10px' }}>{message}</div>}

            <div style={{ display: 'grid', gap: '15px' }}>
                {repos.map(repo => (
                    <div key={repo.id} style={{
                        border: '1px solid #ddd',
                        padding: '15px',
                        borderRadius: '6px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <div>
                            <h3 style={{ margin: '0 0 5px 0' }}>
                                <a href={repo.html_url} target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', textDecoration: 'none' }}>
                                    {repo.full_name}
                                </a>
                            </h3>
                            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>{repo.description}</p>
                        </div>
                        <button
                            onClick={() => addRepo(repo)}
                            disabled={addingRepoId === repo.id}
                            style={{
                                padding: '8px 16px',
                                backgroundColor: addingRepoId === repo.id ? '#9ca3af' : '#10b981',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: addingRepoId === repo.id ? 'not-allowed' : 'pointer',
                                whiteSpace: 'nowrap'
                            }}
                        >
                            {addingRepoId === repo.id ? 'Adding...' : 'Add to Repose'}
                        </button>
                    </div>
                ))}
            </div>
            {repos.length === 0 && !loading && !error && <p>No repositories to show. Click "Fetch Available Repos" to start.</p>}
        </div>
    );
};

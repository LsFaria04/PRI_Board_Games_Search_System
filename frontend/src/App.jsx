import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [numFound, setNumFound] = useState(0)
  const [loading, setLoading] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState('')
  const [searchType, setSearchType] = useState('semantic') // 'semantic' or 'keyword'
  const [page, setPage] = useState(0)

  const apiCommunication = async (isMore) => {
    if (searchType === 'semantic') {
      // Call the semantic search API
      const response = await fetch('http://localhost:5000/api/search/semantic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, page: page })
      })
      const data = await response.json();
      if(isMore){
        setResults(prev => [...prev, ...data.results]);
      }
      else{
        setResults(data.results || []);
      }
      setNumFound(data.numFound || 0);
    } else {
      // Call keyword search API
      const response = await fetch('http://localhost:5000/api/search/keyword', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, page: page })
      })
      const data = await response.json();

      if(isMore){
        setResults(prev => [...prev, ...data.results]);
      }
      else{
        setResults(data.results || []);
      }
      
      setNumFound(data.numFound || 0);
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return

    setLoading(true);
    setError('');
    setResults([]);

    try {
      await apiCommunication(false);
    } catch (err) {
      setError('Failed to fetch results. Make sure the backend API is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleLoadMore = async (e) => {
    e.preventDefault();
    if (!query.trim()) return
    setError('');
    setLoadingMore(true);

    try {
      await apiCommunication(true);
    } catch (err) {
      setError('Failed to fetch results. Make sure the backend API is running.')
      console.error(err);
    } finally {
      setLoadingMore(false);
    }

  }

  useEffect(() => {
    if (query) {
      handleLoadMore(new Event("submit"));
    }
  }, [page]);


  return (
    <div className="app">
      <header className="header">
        <h1 className="title">BoardVerse</h1>
        <p className="subtitle">Discover your next favorite board game</p>
      </header>

      <main className="main">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-container">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for board games..."
              className="search-input"
              autoFocus
            />
            <button type="submit" className="search-button">
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          <div className="search-type">
            <label>
              <input
                type="radio"
                value="semantic"
                checked={searchType === 'semantic'}
                onChange={(e) => setSearchType(e.target.value)}
              />
              Semantic Search
            </label>
            <label>
              <input
                type="radio"
                value="keyword"
                checked={searchType === 'keyword'}
                onChange={(e) => setSearchType(e.target.value)}
              />
              Keyword Search
            </label>
          </div>
        </form>

        {error && <div className="error">{error}</div>}

        {results.length > 0 && (
          <><div className="results">
            <h2>Results ({numFound})</h2>
            <div className="results-grid">
              {results.map((game) => (
                <div key={game.id} className="result-card">
                  <h3>{game.name}</h3>
                  {game.score && <p className="score">Score: {game.score.toFixed(2)}</p>}
                  {game.description && (
                    <p className="description">{game.description.substring(0, 150)}...</p>
                  )}
                  {game.yearpublished && (
                    <p className="meta">Published: {game.yearpublished}</p>
                  )}
                  {game.average && (
                    <p className="meta">Rating: {game.average.toFixed(2)}/10</p>
                  )}
                </div>
              ))}
            </div>
          </div><button onClick={() => setPage(page + 1)}> {loadingMore ? 'Loading ...' : 'Load More'} </button></>
        )}

        {!loading && query && results.length === 0 && !error && (
          <div className="no-results">No games found. Try a different search.</div>
        )}
      </main>
    </div>
  )
}

export default App

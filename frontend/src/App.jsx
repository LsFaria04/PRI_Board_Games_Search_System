import { useState, useEffect } from 'react'
import './App.css'
import GameModal from './components/gameModal'

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [numFound, setNumFound] = useState(0)
  const [loading, setLoading] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState('')
  const [searchType, setSearchType] = useState('hybrid')
  const [page, setPage] = useState(0)
  const [selectedGame, setSelectedGame] = useState(null)

  const apiCommunication = async (isMore) => {
    const endpoint =
      searchType === 'semantic'
        ? 'http://localhost:5000/api/search/semantic'
        : (searchType === "hybrid" ? 'http://localhost:5000/api/search/hybrid' : 'http://localhost:5000/api/search/keyword') 

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, page })
    })

    const data = await response.json()
    console.log(data)
    if (isMore) {
      setResults(prev => [...prev, ...data.results])
    } else {
      setResults(data.results || [])
    }
    setNumFound(data.numFound || 0)
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResults([])
    setPage(0) 

    try {
      await apiCommunication(false)
    } catch (err) {
      setError('Failed to fetch results. Make sure the backend API is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (query && page > 0) {
      setLoadingMore(true)
      apiCommunication(true)
        .catch(err => {
          setError('Failed to fetch results. Make sure the backend API is running.')
          console.error(err)
        })
        .finally(() => setLoadingMore(false))
    }
  }, [page])

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
                value="hybrid"
                checked={searchType === 'hybrid'}
                onChange={(e) => setSearchType(e.target.value)}
              />
              Hybrid Search
            </label>
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
          <>
            <div className="results">
              <h2>Results ({numFound})</h2>
              <div className="results-grid">
                {results.map((game) => (
                  <div
                    key={game.id}
                    className="result-card"
                    onClick={() => setSelectedGame(game)}
                  >
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
            </div>
            <button onClick={() => setPage(page + 1)}>
              {loadingMore ? 'Loading ...' : 'Load More'}
            </button>
          </>
        )}

        <GameModal isOpen={!!selectedGame} onClose={() => setSelectedGame(null)}>
          {selectedGame && (
            <>
              <div className="game-modal-body">
                {/* Title & Description */}
                <h2 className="game-title">{selectedGame.name}</h2>
                <p className="description">{selectedGame.description}</p>

                {/* Core Info */}
                <section className="game-section">
                  <h3>Overview</h3>
                  <ul className="meta-list">
                    <li><strong>Alternative Names:</strong> {selectedGame.alt_names ? selectedGame.alt_names.join(', ') : ""}</li>
                    <li><strong>Published:</strong> {selectedGame.yearpublished}</li>
                    <li><strong>Rating:</strong> {selectedGame.average?.toFixed(2)}/10</li>
                    <li><strong>Weight:</strong> {selectedGame.averageweight}</li>
                  </ul>
                </section>

                {/* Play Info */}
                <section className="game-section">
                  <h3>Play Details</h3>
                  <ul className="meta-list">
                    <li><strong>Minimum Age:</strong> {selectedGame.minage}</li>
                    <li><strong>Players:</strong> {selectedGame.minplayers} - {selectedGame.maxplayers}</li>
                    <li><strong>Playing Time:</strong> {selectedGame.playingtime}</li>
                  </ul>
                </section>

                {/* Contributors */}
                <section className="game-section">
                  <h3>Creators</h3>
                  <ul className="meta-list">
                    <li><strong>Publishers:</strong> {selectedGame.publishers ? selectedGame.publishers.join(', ') : ""}</li>
                    <li><strong>Designers:</strong> {selectedGame.designers ? selectedGame.designers.join(', ') : ""}</li>
                    <li><strong>Artists:</strong> {selectedGame.artists ? selectedGame.artists.join(', ') : ""}</li>
                  </ul>
                </section>

                {/* Classification */}
                <section className="game-section">
                  <h3>Categories & Mechanics</h3>
                  <ul className="meta-list">
                    <li><strong>Categories:</strong> {selectedGame.categories ? selectedGame.categories.join(', ') : ""}</li>
                    <li><strong>Mechanics:</strong> {selectedGame.mechanics ? selectedGame.mechanics.join(', ') : ""}</li>
                    <li><strong>Families:</strong> {selectedGame.families ? selectedGame.families.join(', ') : ""}</li>
                    <li><strong>Expansions:</strong> {selectedGame.expansions ? selectedGame.expansions.join(', ') : ""}</li>
                  </ul>
                </section>

                {/* Community Info */}
                <section className="game-section">
                  <h3>Community</h3>
                  <ul className="meta-list">
                    <li><strong>Owned by:</strong> {selectedGame.owned}</li>
                    <li><strong>Trading:</strong> {selectedGame.trading}</li>
                    <li><strong>Wanting to Trade:</strong> {selectedGame.wanting}</li>
                    <li><strong>Wishing to Buy:</strong> {selectedGame.wishing}</li>
                  </ul>
                </section>
              </div>
              </>

          )}
        </GameModal>

        {!loading && query && results.length === 0 && !error && (
          <div className="no-results">No games found. Try a different search.</div>
        )}
      </main>
    </div>
  )
}

export default App
